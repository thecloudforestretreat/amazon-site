// Secrets belong in Pages environment bindings, never in generated HTML.
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const stagingHost = 'staging.experiencetheamazon.com';
const allowedHosts = new Set([stagingHost, 'experiencetheamazon.com', 'www.experiencetheamazon.com']);
const json = (body, status = 200) => Response.json(body, {status, headers: {'Cache-Control':'no-store','X-Robots-Tag':'noindex, nofollow','X-Content-Type-Options':'nosniff'}});
const escapeHtml = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const countryLabel = value => ({not_sure:'Not sure yet',ecuador:'Ecuador',peru:'Peru',bolivia:'Bolivia',brazil:'Brazil',colombia:'Colombia',guyana:'Guyana',suriname:'Suriname',venezuela:'Venezuela'}[value] || value);
export function inquiryHtml(p) {
  const rows = [['Name',p.first_name+' '+p.last_name],['Email',p.email],['Phone',p.phone || '—'],['Country',countryLabel(p.country)],['Guests',p.travelers || '—'],['Dates',p.start_date+' → '+p.end_date],['Language',p.language]];
  return `<div style="background:#f8f5ec;padding:28px;font-family:Arial,sans-serif;color:#15392e"><div style="max-width:600px;margin:auto;background:#fff;padding:28px;border-radius:16px"><p style="color:#65796d;font-size:12px;letter-spacing:2px">TRIP PLANNING</p><h1 style="font-family:Georgia,serif;font-size:28px">A new Amazon inquiry</h1><table style="width:100%;border-collapse:collapse">${rows.map(([label,value])=>`<tr><th style="text-align:left;padding:9px 0;border-bottom:1px solid #eee">${label}</th><td style="padding:9px 0;border-bottom:1px solid #eee">${escapeHtml(value)}</td></tr>`).join('')}</table><p style="white-space:pre-wrap;line-height:1.6">${escapeHtml(p.interests)}</p><p style="font-size:12px;color:#65796d">Consent: inquiry response only. Reply to this email to contact the traveler.</p><table role="presentation" cellpadding="0" cellspacing="0" style="margin-top:26px;font-family:Arial,sans-serif;color:#15392e"><tr><td style="vertical-align:top;padding-right:16px"><a href="https://experiencetheamazon.com/"><img src="https://experiencetheamazon.com/assets/logo/eta_logo_trans_256.png" width="80" height="80" alt="Experience The Amazon" style="display:block;border:0"></a></td><td style="vertical-align:top;border-left:2px solid #d5a340;padding-left:16px"><a href="https://experiencetheamazon.com/" style="font-family:Georgia,serif;font-size:24px;line-height:25px;font-weight:bold;color:#15392e;text-decoration:none">Experience<br>The Amazon</a><p style="font-size:12px;line-height:18px;margin:10px 0">Your journey into the Amazon starts here.</p><p style="margin:10px 0;font-size:13px"><a href="https://experiencetheamazon.com/" style="color:#15392e;font-weight:bold;text-decoration:none">Explore the Amazon →</a></p><table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="padding-right:16px"><a href="https://wa.me/593969076501" style="color:#15392e;text-decoration:none;font-size:12px;font-weight:bold"><img src="https://experiencetheamazon.com/assets/images/email/whatsapp.png" width="18" height="18" alt="" style="vertical-align:middle;border:0"> WhatsApp</a></td><td><a href="https://www.instagram.com/experienceamazon/" style="color:#15392e;text-decoration:none;font-size:12px;font-weight:bold"><img src="https://experiencetheamazon.com/assets/images/email/instagram.png" width="18" height="18" alt="" style="vertical-align:middle;border:0"> Instagram</a></td></tr></table></td></tr></table></div></div>`;
}
export function ready(env) {
  return env.CONTACT_ENABLED === 'true' && ['TURNSTILE_SITE_KEY','TURNSTILE_SECRET_KEY','BREVO_API_KEY','CONTACT_FROM','CONTACT_TO'].every(k => typeof env[k] === 'string' && env[k].trim()) && emailPattern.test(env.CONTACT_FROM) && emailPattern.test(env.CONTACT_TO);
}
export async function handleContact(request, env, send = fetch) {
  const url = new URL(request.url);
  const host = env.CONTACT_HOSTNAME || stagingHost;
  if (!allowedHosts.has(host)) return json({error:'host_not_allowed'},403);
  if (url.hostname !== host) return json({error:'host_not_allowed'},403);
  if (request.method === 'GET') return json({enabled:ready(env), siteKey:env.TURNSTILE_SITE_KEY && env.TURNSTILE_SECRET_KEY ? env.TURNSTILE_SITE_KEY : null});
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
  const fields = {first_name:80,last_name:120,email:254,country:30,travelers:2,phone:32,start_date:10,end_date:10,interests:4000,language:2};
  if (!p || typeof p !== 'object' || Array.isArray(p)) return json({error:'invalid_fields'},400);
  for (const [key,max] of Object.entries(fields)) {
    if (typeof p[key] !== 'string' || p[key].length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(p[key])) return json({error:'invalid_fields'},400);
    p[key] = p[key].trim();
  }
  if (p.website || !p.first_name || !p.last_name || !emailPattern.test(p.email) || p.privacy_consent !== 'yes' || !['en','es'].includes(p.language) || !['not_sure','ecuador','peru','bolivia','brazil','colombia','guyana','suriname','venezuela'].includes(p.country) || (p.travelers && (!/^\d+$/.test(p.travelers) || +p.travelers<1 || +p.travelers>99))) return json({error:'invalid_fields'},400);
  const parts = new Intl.DateTimeFormat('en-US', {timeZone:'America/Guayaquil',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
  const part = type => parts.find(p => p.type === type).value;
  const today = part('year') + '-' + part('month') + '-' + part('day');
  const validDate = value => /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value+'T00:00:00Z')) && new Date(value+'T00:00:00Z').toISOString().slice(0,10) === value;
  if (!validDate(p.start_date) || !validDate(p.end_date) || p.start_date < today || p.end_date < p.start_date) return json({error:'invalid_dates'},400);
  for (const key of ['first_name','last_name']) p[key] = p[key].replace(/^\p{L}/u, letter => letter.toLocaleUpperCase(p.language));
  const fullName = p.first_name + ' ' + p.last_name;
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
      body:JSON.stringify({sender:{email:env.CONTACT_FROM,name:'Experience The Amazon'},to:[{email:env.CONTACT_TO}],replyTo:{email:p.email,name:fullName},subject:'Amazon trip inquiry · '+countryLabel(p.country),
        htmlContent:inquiryHtml(p),
        textContent:`First name: ${p.first_name}\nLast name: ${p.last_name}\nEmail: ${p.email}\nLanguage: ${p.language}\nCountry: ${countryLabel(p.country)}\nTravelers: ${p.travelers}\nPhone: ${p.phone}\nStart date: ${p.start_date}\nEnd date: ${p.end_date}\n\n${p.interests}\n\nConsent: inquiry response only\n\nExperience The Amazon\nYour journey into the Amazon starts here.\nhttps://experiencetheamazon.com\ninfo@experiencetheamazon.com\nWhatsApp: https://wa.me/593969076501\nInstagram: https://www.instagram.com/experienceamazon/`})
    });
    if (!response.ok) return json({error:'delivery_failed'},502);
    const accepted = await response.json();
    if (typeof accepted.messageId !== 'string' || !accepted.messageId) return json({error:'delivery_failed'},502);
    // API acceptance means queued, not proven inbox delivery.
    return json({ok:true,status:'queued'});
  } catch {return json({error:'service_unavailable'},502);}
}
export const onRequest = ({request,env}) => handleContact(request,env);
