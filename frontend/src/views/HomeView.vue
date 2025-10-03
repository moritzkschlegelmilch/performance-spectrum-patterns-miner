<template>
  <div v-html="html" class="markdown-body"></div>
</template>

<script setup lang="js">
import markdownit from 'markdown-it'
import markdownItAnchor from 'markdown-it-anchor'

// 1) Load the markdown as raw text
import content from '../../../README.md?raw'

// 2) Tell Vite to bundle the images and give us their emitted URLs
//    IMPORTANT: make the pattern(s) match where your MD refers to images.
//    Example assumes your MD uses paths like "./manual/images/foo.png"
const assetMap = import.meta.glob(
    // adjust these globs to match your repo layout
    [
        '../../../manual/images/**/*.{png,jpg,jpeg,gif,svg,webp,apng}',
        '../../../**/*.{png,jpg,jpeg,gif,svg,webp,apng}'
    ],
    { eager: true, import: 'default' }
)
// assetMap keys are the *import specifiers* (the path strings matched by the globs).
// Values are emitted URLs (e.g. "/assets/logo.abc123.png").

// 3) Helper to resolve a Markdown-authored relative path to an emitted URL.
//    We’ll map authoring paths like "./manual/images/logo.png"
//    to the corresponding glob key(s) we imported above.
function resolveAsset(authorPath) {
    // normalize leading "./"
    const clean = authorPath.replace(/^\.\//, '')

    // Try a few prefixes that match your globs. Tweak as needed.
    const candidates = [
        `../../../${clean}`,                   // relative to *this component* file
        `../../../manual/images/${clean.replace(/^manual\/images\//, '')}`
    ]

    for (const key of candidates) {
        if (assetMap[key]) return assetMap[key]
    }
    return null // not found -> leave as-is
}

const md = markdownit({ html: true })
.use(markdownItAnchor, {
    slugify: s => s.trim().toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
})

// 4) Also rewrite Markdown image tokens (![alt](...))
const defaultImage = md.renderer.rules.image
md.renderer.rules.image = (tokens, idx, options, env, self) => {
    const token = tokens[idx]
    const src = token.attrGet('src') || ''
    const isRelative = !/^(?:[a-z][a-z0-9+.-]*:|\/)/i.test(src) // not http(s):, data:, or root-absolute
    if (isRelative) {
        const url = resolveAsset(src)
        if (url) token.attrSet('src', url)
    }
    return defaultImage
        ? defaultImage(tokens, idx, options, env, self)
        : self.renderToken(tokens, idx, options)
}

// 5) Render Markdown, then rewrite any raw <img> tags inside HTML
function rewriteHtmlImages(html) {
    const doc = new DOMParser().parseFromString(html, 'text/html')
    const imgs = doc.querySelectorAll('img[src]')
    imgs.forEach(img => {
        const src = img.getAttribute('src') || ''
        const isRelative = !/^(?:[a-z][a-z0-9+.-]*:|\/)/i.test(src)
        if (isRelative) {
            const url = resolveAsset(src)
            if (url) img.setAttribute('src', url)
        }
    })
    return doc.body.innerHTML
}

const html = rewriteHtmlImages(md.render(content))
</script>

<style>
.markdown-body {
    background-color: #0d1117;
    color: #c9d1d9;
    padding: 2rem;
    line-height: 1.7;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    word-wrap: break-word;
}

/* Headings */
.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 600;
    line-height: 1.25;
    scroll-margin-top: 80px;
}

.markdown-body h1 {
    font-size: 2em;
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.3em;
}
.markdown-body h2 {
    font-size: 1.5em;
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.3em;
}
.markdown-body h3 { font-size: 1.25em; }
.markdown-body h4 { font-size: 1.1em; }
.markdown-body h5 { font-size: 1em; }
.markdown-body h6 { font-size: 0.9em; color: #8b949e; }

/* Paragraphs and line breaks */
.markdown-body p {
    margin: 1em 0;
}

/* Inline code */
.markdown-body code {
    background-color: rgba(110, 118, 129, 0.4);
    padding: 0.2em 0.4em;
    font-size: 85%;
    border-radius: 6px;
    color: #c9d1d9;
}

/* Code blocks */
.markdown-body pre {
    background-color: #161b22;
    padding: 1em;
    overflow: auto;
    font-size: 85%;
    border-radius: 6px;
    line-height: 1.5;
    color: #c9d1d9;
}

.markdown-body pre code {
    background: none;
    padding: 0;
    color: inherit;
}

/* Blockquotes */
.markdown-body blockquote {
    margin: 1em 0;
    padding-left: 1em;
    border-left: 0.25em solid #30363d;
    color: #8b949e;
    background-color: #161b22;
}

/* Tables */
.markdown-body table {
    border-collapse: collapse;
    width: 100%;
    overflow: auto;
    display: block;
    margin: 1.5em 0;
}

.markdown-body th,
.markdown-body td {
    border: 1px solid #30363d;
    padding: 0.6em 1em;
    text-align: left;
}

.markdown-body th {
    background-color: #21262d;
    font-weight: 600;
}

.markdown-body tr:nth-child(2n) {
    background-color: #161b22;
}

/* Lists */
.markdown-body ul,
.markdown-body ol {
    padding-left: 2em;
    margin: 1em 0;
}

.markdown-body li {
    margin: 0.3em 0;
}

/* Links */
.markdown-body a {
    color: #58a6ff;
    text-decoration: none;
}

.markdown-body a:hover {
    text-decoration: underline;
}

/* Images */
.markdown-body img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em 0;
}

/* Horizontal rule */
.markdown-body hr {
    border: 0;
    height: 1px;
    background: #30363d;
    margin: 2em 0;
}


</style>