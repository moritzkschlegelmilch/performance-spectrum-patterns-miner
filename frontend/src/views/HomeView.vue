<template>
  <div v-html="html" class="markdown-body"></div>
</template>
<script setup lang="js">
import { onMounted } from 'vue'
import markdownit from 'markdown-it'
import markdownItAnchor from 'markdown-it-anchor'
import {html} from '../composables/useReadmeState.js'

const md = markdownit({ html: true }).use(markdownItAnchor, {
    slugify: s => s.trim().toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
})

function toAbsoluteUrl(src) {
    if (!src) return src
    if (/^(?:[a-z][a-z0-9+.-]*:|\/\/|\/)/i.test(src)) return src
    return import.meta.env.VITE_RAW_BASE_URL + src.replace(/^\.\//, '')
}

const defaultImage = md.renderer.rules.image
md.renderer.rules.image = (tokens, idx, options, env, self) => {
    const token = tokens[idx]
    const src = token.attrGet('src') || ''
    token.attrSet('src', toAbsoluteUrl(src))

    return defaultImage
        ? defaultImage(tokens, idx, options, env, self)
        : self.renderToken(tokens, idx, options)
}

function rewriteHtmlImages(renderedHtml) {
    const doc = new DOMParser().parseFromString(renderedHtml, 'text/html')
    const imgs = doc.querySelectorAll('img[src]')

    imgs.forEach(img => {
        const src = img.getAttribute('src') || ''
        img.setAttribute('src', toAbsoluteUrl(src))
    })

    return doc.body.innerHTML
}

onMounted(async () => {
    try {
        const res = await fetch(import.meta.env.VITE_README_URL)
        const content = await res.text()
        html.value = rewriteHtmlImages(md.render(content))
    } catch (err) {
        html.value = '<p>Failed to load README.</p>'
        console.error(err)
    }
})
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