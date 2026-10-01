#!/usr/bin/env node
/* Diagnostic d'une source : affiche ce que renvoie le site pour adapter l'analyseur.
 * Usage : node scripts/debug-source.mjs decathlon,maparami */
import { readFile } from "node:fs/promises";
import { parseAnyHtml } from "./lib/parsers.mjs";

const ids = (process.argv[2] || "").split(",").filter(Boolean);
const { sources } = JSON.parse(await readFile(new URL("../sources.json", import.meta.url), "utf8"));
const UA = "Mozilla/5.0 (compatible; PromoMarocBot/1.0; +https://github.com/medamineamzil-design/ebookclassics-files)";

for (const src of sources.filter((s) => ids.includes(s.id))) {
  console.log(`\n===== ${src.id} : ${src.promoUrl}`);
  for (const url of [src.promoUrl, src.url.replace(/\/$/, "") + "/products.json?limit=1", src.url.replace(/\/$/, "") + "/wp-json/wc/store/v1/products?per_page=1"]) {
    try {
      const res = await fetch(url, { headers: { "User-Agent": UA, "Accept-Language": "fr-MA,fr;q=0.9" }, redirect: "follow" });
      const body = await res.text();
      console.log(`-- ${url}\n   HTTP ${res.status} → ${res.url}\n   type=${res.headers.get("content-type")} server=${res.headers.get("server")} taille=${body.length}`);
      if (url !== src.promoUrl) { console.log("   début : " + body.slice(0, 200).replace(/\s+/g, " ")); continue; }
      const marks = ["product-miniature", "product-item", 'class="prd', "woocommerce", "cdn.shopify", "__NEXT_DATA__", "application/ld+json", "regular-price", "old-price", "oldPrice", "price--compare", "<del", "data-price", "prestashop", "Magento", "vtex", "salesforce", "algolia"];
      console.log("   marqueurs : " + marks.map((m) => `${m}=${body.split(m).length - 1}`).join(" "));
      console.log("   titre : " + (body.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1]?.trim());
      const res2 = parseAnyHtml(body, src.promoUrl);
      console.log(`   analyseur : ${res2.platform} ${res2.items.length} produits`);
      const anchor = body.search(/data-testid="current-price"|regular-price/);
      if (anchor > 0) {
        const start = Math.max(body.lastIndexOf("product-card", anchor - 1) - 200, anchor - 3000, 0);
        console.log("   carte produit complète : " + body.slice(start, anchor + 1800).replace(/\s+/g, " "));
      }
      const re = /(regular-price|old-price|oldPrice|price--compare|<del|data-price|class="[^"]*price[^"]*")/gi;
      let m, n = 0;
      while ((m = re.exec(body)) && n < 4) { console.log("   extrait : " + body.slice(Math.max(0, m.index - 400), m.index + 300).replace(/\s+/g, " ")); n++; re.lastIndex = m.index + 2000; }
    } catch (e) {
      console.log(`-- ${url}\n   erreur : ${e.message}`);
    }
  }
}
