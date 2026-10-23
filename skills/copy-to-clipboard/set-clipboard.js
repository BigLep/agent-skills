// Sets the macOS clipboard to an HTML flavor plus a plain-text fallback.
// Usage: CLIP_HTML="..." CLIP_TEXT="..." osascript -l JavaScript set-clipboard.js
ObjC.import('AppKit');
function run() {
  const env = $.NSProcessInfo.processInfo.environment;
  const html = env.objectForKey('CLIP_HTML');
  const text = env.objectForKey('CLIP_TEXT');
  if (html.isNil() || text.isNil() || html.length === 0 || text.length === 0) {
    throw new Error('CLIP_HTML and CLIP_TEXT must both be set and non-empty');
  }
  const pb = $.NSPasteboard.generalPasteboard;
  pb.clearContents;
  const okHtml = pb.setStringForType(html, $.NSPasteboardTypeHTML);
  const okText = pb.setStringForType(text, $.NSPasteboardTypeString);
  if (!okHtml || !okText) throw new Error('Failed to write clipboard');
  return 'ok: html=' + html.length + ' chars, text=' + text.length + ' chars';
}
