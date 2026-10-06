// Secrets belong in Pages environment bindings, never in generated HTML.
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const host = 'staging.experiencetheamazon.com';
const json = (body, status = 200) => Response.json(body, {status, headers: {'Cache-Control':'no-store','X-Robots-Tag':'noindex, nofollow','X-Content-Type-Options':'nosniff'}});
export function ready(env) {
  return env.CONTACT_ENABLED === 'true' && ['TURNSTILE_SITE_KEY','TURNSTILE_SECRET_KEY','BREVO_API_KEY','CONTACT_FROM','CONTACT_TO'].every(k => typeof env[k] === 'string' && env[k].trim()) && emailPattern.test(env.CONTACT_FROM) && emailPattern.test(env.CONTACT_TO);
}
export async function handleContact(request, env, send = fetch) {
  const url = new URL(request.url);
  if (url.hostname !== host) return json({error:'host_not_allowed'},403);
  if (request.method === 'GET') return json({enabled:ready(env), siteKey:ready(env) ? env.TURNSTILE_SITE_KEY : null});
  if (request.method !== 'POST') return json({error:'method_not_allowed'},405);
  if (request.headers.get('Origin') !== url.origin) return json({error:'origin_not_allowed'},403);
  if (!ready(env)) return json({error:'unavailable'},503);
  if (!(request.headers.get('Content-Type') || '').startsWith('application/json')) return json({error:'invalid_content_type'},415);
  // Bound body reads even when Content-Length is omitted or dishonest.
  const reader = request.body?.getReader();
  if (!reader) return json({error:'invalid_fields'},400);
  let size = 0; const chunks = [];
  while (true) {
    const {value,done} = await reader.read(); if (done) break;
    size += value.byteLength; if (size > 16384) {await reader.cancel(); return json({error:'too_large'},413);} chunks.push(value);
  }
  const bytes = new Uint8Array(size); let offset = 0; for (const chunk of chunks) {bytes.set(chunk,offset); offset += chunk.length;}
  let p; try {p = JSON.parse(new TextDecoder().decode(bytes));} catch {return json({error:'invalid_json'},400);}
  const fields = {name:120,email:254,country:30,travelers:2,dates:160,interests:4000,language:2};
  if (!p || typeof p !== 'object' || Array.isArray(p)) return json({error:'invalid_fields'},400);
  for (const [key,max] of Object.entries(fields)) {
    if (typeof p[key] !== 'string' || p[key].length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(p[key])) return json({error:'invalid_fields'},400);
    p[key] = p[key].trim();
  }
  if (p.website || !p.name || !emailPattern.test(p.email) || p.privacy_consent !== 'yes' || !['en','es'].includes(p.language) || !['not_sure','ecuador','peru','bolivia','brazil','colombia'].includes(p.country) || (p.travelers && (!/^\d+$/.test(p.travelers) || +p.travelers<1 || +p.travelers>30))) return json({error:'invalid_fields'},400);
  const token = p['cf-turnstile-response'];
  if (typeof token !== 'string' || !token || token.length > 2048) return json({error:'verification_required'},400);
  try {
    const verification = await send('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method:'POST',headers:{'Content-Type':'application/json'},signal:AbortSignal.timeout(10000),
      body:JSON.stringify({secret:env.TURNSTILE_SECRET_KEY,response:token,remoteip:request.headers.get('CF-Connecting-IP') || undefined})
    });
    if (!verification.ok) return json({error:'verification_unavailable'},502);
    const result = await verification.json();
    if (result.success !== true || result.hostname !== host || result.action !== 'contact') return json({error:'verification_failed'},400);
    const response = await send('https://api.brevo.com/v3/smtp/email', {
      method:'POST',headers:{'Content-Type':'application/json','api-key':env.BREVO_API_KEY},signal:AbortSignal.timeout(10000),
      body:JSON.stringify({sender:{email:env.CONTACT_FROM,name:'Experience The Amazon'},to:[{email:env.CONTACT_TO}],replyTo:{email:p.email,name:p.name},subject:'Amazon trip inquiry · '+p.country,
        textContent:`Name: ${p.name}\nEmail: ${p.email}\nLanguage: ${p.language}\nCountry: ${p.country}\nTravelers: ${p.travelers}\nDates: ${p.dates}\n\n${p.interests}\n\nConsent: inquiry response only`})
    });
    if (!response.ok) return json({error:'delivery_failed'},502);
    const accepted = await response.json();
    if (typeof accepted.messageId !== 'string' || !accepted.messageId) return json({error:'delivery_failed'},502);
    // API acceptance means queued, not proven inbox delivery.
    return json({ok:true,status:'queued'});
  } catch {return json({error:'service_unavailable'},502);}
}
export const onRequest = ({request,env}) => handleContact(request,env);
