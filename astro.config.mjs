// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://jamieatlas.com',
  // One URL per page (doc 69 item 3): canonical, sitemap and every internal
  // link say /studio, never /studio/. Vercel gets the matching setting.
  trailingSlash: 'never',
  integrations: [sitemap()],
  vite: {
    plugins: [tailwindcss()],
  },
});
