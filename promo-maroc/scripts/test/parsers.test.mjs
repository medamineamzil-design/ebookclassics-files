import { test } from "node:test";
import assert from "node:assert/strict";
import { parsePrice, parseShopify, parseWooStore, parseJumia, parsePrestashop, parseMagento, parseWooHtml, parseAnyHtml, isValidPromo, guessCategory } from "../lib/parsers.mjs";

test("parsePrice gère les formats marocains", () => {
  assert.equal(parsePrice("1 299,00 DH"), 1299);
  assert.equal(parsePrice("1.299,50 Dhs"), 1299.5);
  assert.equal(parsePrice("2,499.00 MAD"), 2499);
  assert.equal(parsePrice("179 Dhs"), 179);
  assert.equal(parsePrice("1.299 DH"), 1299);
  assert.equal(parsePrice("19,90"), 19.9);
  assert.equal(parsePrice("12 990,00 DH"), 12990);
  assert.ok(Number.isNaN(parsePrice("")));
});

test("Shopify : garde les variantes avec compare_at_price", () => {
  const items = parseShopify({ products: [
    { title: "Crème CeraVe", vendor: "CeraVe", handle: "creme", images: [{ src: "https://x/i.jpg" }], variants: [{ price: "120.00", compare_at_price: "150.00" }] },
    { title: "Sans promo", handle: "n", variants: [{ price: "10.00", compare_at_price: null }] }
  ] }, "https://shop.ma");
  assert.equal(items.length, 1);
  assert.deepEqual(items[0], { product: "Crème CeraVe", brand: "CeraVe", originalPrice: 150, promoPrice: 120, url: "https://shop.ma/products/creme", image: "https://x/i.jpg" });
});

test("WooCommerce Store API", () => {
  const items = parseWooStore([{ name: "Mixeur", permalink: "https://s.ma/p/mixeur", prices: { regular_price: "49900", sale_price: "39900", currency_minor_unit: 2 }, images: [] }]);
  assert.equal(items[0].originalPrice, 499);
  assert.equal(items[0].promoPrice, 399);
});

test("Jumia", () => {
  const html = `<div><article class="prd _fb col c-prd"><a class="core" href="/sandales-adidas-123.html" data-gtm-brand="Adidas"><div class="img-c"><img data-src="https://ma.jumia.is/a.jpg" class="img"></div>
    <div class="info"><h3 class="name">Adidas Adilette Aqua</h3><div class="prc">179 Dhs</div><div class="s-prc-w"><div class="old">300 Dhs</div><div class="bdg _dsct _sm">40%</div></div></div></a></article>
    <article class="prd _fb col c-prd"><a class="core" href="/x.html"><h3 class="name">Sans ancien prix</h3><div class="prc">99 Dhs</div></a></article></div>`;
  const items = parseJumia(html, "https://www.jumia.ma/flash-sales/");
  assert.equal(items.length, 1);
  assert.deepEqual(items[0], { product: "Adidas Adilette Aqua", brand: "Adidas", originalPrice: 300, promoPrice: 179, url: "https://www.jumia.ma/sandales-adidas-123.html", image: "https://ma.jumia.is/a.jpg" });
});

test("PrestaShop", () => {
  const html = `<article class="product-miniature js-product-miniature" data-id-product="1"><img src="/img/1.jpg">
    <h3 class="h3 product-title"><a href="https://d.ma/velo.html">Vélo VTT</a></h3>
    <span class="regular-price">2 999,00 DH</span><span class="price">2 499,00 DH</span></article>`;
  const items = parsePrestashop(html, "https://d.ma/5080-promotions");
  assert.equal(items.length, 1);
  assert.equal(items[0].product, "Vélo VTT");
  assert.equal(items[0].originalPrice, 2999);
  assert.equal(items[0].promoPrice, 2499);
  assert.equal(items[0].image, "https://d.ma/img/1.jpg");
});

test("Magento", () => {
  const html = `<li class="item product product-item"><img class="product-image-photo" src="https://e.ma/m.jpg">
    <a class="product-item-link" href="https://e.ma/tv.html"> TV LG 55" </a>
    <span data-price-amount="4990" data-price-type="finalPrice"></span><span data-price-type="oldPrice" data-price-amount="6490"></span></li>`;
  const items = parseMagento(html, "https://e.ma/vente-flash");
  assert.deepEqual(items[0], { product: 'TV LG 55"', brand: "", originalPrice: 6490, promoPrice: 4990, url: "https://e.ma/tv.html", image: "https://e.ma/m.jpg" });
});

test("WooCommerce HTML et détection automatique", () => {
  const html = `<ul><li class="product type-product"><a href="https://p.ma/creme"><img src="https://p.ma/c.jpg"><h2 class="woocommerce-loop-product__title">Crème solaire</h2>
    <span class="price"><del><bdi>189,00&nbsp;DH</bdi></del> <ins><bdi>151,20&nbsp;DH</bdi></ins></span></a></li></ul>`;
  assert.equal(parseWooHtml(html, "https://p.ma").length, 1);
  const any = parseAnyHtml(html, "https://p.ma");
  assert.equal(any.platform, "woocommerce-html");
  assert.equal(any.items[0].promoPrice, 151.2);
});

test("validation et catégories", () => {
  assert.ok(isValidPromo({ product: "Abc", originalPrice: 100, promoPrice: 80 }));
  assert.ok(!isValidPromo({ product: "Abc", originalPrice: 80, promoPrice: 100 }));
  assert.ok(!isValidPromo({ product: "Abc", originalPrice: 100, promoPrice: 1 }));
  assert.equal(guessCategory("Smartphone Samsung Galaxy A15"), "high-tech");
  assert.equal(guessCategory("Machine à laver Beko 8kg"), "electromenager");
  assert.equal(guessCategory("Huile de table Lesieur 5L"), "alimentation");
  assert.equal(guessCategory("Truc inconnu", "sante"), "sante");
});
