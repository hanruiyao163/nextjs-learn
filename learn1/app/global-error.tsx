'use client';
function GlobalError({error}: {error: Error & {digest?: string}}) {
  return (
    <html>
    <body>
        <h2>Global Error</h2>
    </body>
    </html>
  )
}
export default GlobalError