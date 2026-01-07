"""
Competitor websites configuration.
Each brand has URL(s) and CSS selectors for product extraction.
"""

COMPETITORS = {
    "3P": {
        "urls": [
            "https://3psalads.gr/product-category/sauces/",
            "https://3psalads.gr/product-category/mayonnaise/",
            "https://3psalads.gr/product-category/salad-dressings/",
        ],
        "product_selector": "li.product, .wp-block-post-template li",
        "name_selector": "h2.woocommerce-loop-product__title, h3, .wp-block-post-title",
        "image_selector": "img.attachment-woocommerce_thumbnail, .wp-block-image img",
        "link_selector": "a.woocommerce-LoopProduct-link",
        "needs_js": False,
        "headers": {"Referer": "https://3psalads.gr/"},
        "social": ["https://www.facebook.com/3Psalad/"],
    },
    "Brava": {
        "urls": ["https://minerva.com.gr/proionta/brava/"],
        "product_selector": ".item, [class*='product']",
        "name_selector": "h3, h2, .title",
        "image_selector": "img",
        "link_selector": "a",
        "needs_js": True,
        "social": ["https://www.facebook.com/BravaProducts/"],
    },
    "Colona": {
        "urls": [
            "https://www.colona.be/produit/mayonnaise/",
            "https://www.colona.be/produit/ketchup/",
            "https://www.colona.be/produit/moutarde/",
        ],
        "product_selector": ".produit-card, .product-item, article.produit",
        "name_selector": "h2, h3, .produit-title",
        "image_selector": "img",
        "link_selector": "a",
        "needs_js": False,
        "social": ["https://www.facebook.com/Colona.be/"],
    },
    "Condito": {
        "urls": ["https://conditofoods.com/shop/"],
        "product_selector": "li.product",
        "name_selector": ".woocommerce-loop-product__title",
        "image_selector": "img.attachment-woocommerce_thumbnail",
        "link_selector": "a.woocommerce-LoopProduct-link",
        "needs_js": False,
        "social": ["https://www.facebook.com/conditofoods/"],
    },
    "Delicatessen17": {
        "urls": ["https://www.kalas.gr/products"],
        "product_selector": ".product-card, .product-item, article",
        "name_selector": "h2, h3, .product-title",
        "image_selector": "img",
        "link_selector": "a",
        "needs_js": True,
        "social": ["https://www.facebook.com/kalasgroup/"],
    },
    "Delicia": {
        "urls": ["https://minerva.com.gr/proionta/delicia/"],
        "product_selector": ".elementor-post, .jet-listing-grid__item",
        "name_selector": ".elementor-post__title, h3.elementor-heading-title",
        "image_selector": ".elementor-post__thumbnail img",
        "link_selector": ".elementor-post__thumbnail a",
        "needs_js": True,
        "social": [],
    },
    "Develey": {
        "urls": ["https://www.develey.com/en/products/"],
        "product_selector": ".product-teaser, .teaser-item, article",
        "name_selector": "h2, h3, .teaser-title",
        "image_selector": "img",
        "link_selector": "a",
        "needs_js": True,
        "social": ["https://www.facebook.com/develeyusa/"],
    },
    "Heinz": {
        "urls": ["https://www.heinz.com/el-GR/products"],
        "product_selector": "[data-testid='product-card'], .product-card, article",
        "name_selector": "h2, h3, [data-testid='product-name']",
        "image_selector": "img",
        "link_selector": "a[href*='/προϊόντα/']",
        "needs_js": True,
        "social": ["https://www.facebook.com/HeinzGreece/"],
    },
    "Kyknos": {
        "urls": [
            "https://kyknoscanning.com/el/proionta-tomatas/",
            "https://kyknoscanning.com/el/magionezes-moystardes/",
            "https://kyknoscanning.com/el/ketchup-saltses/",
        ],
        "product_selector": "a[href*='.html']",
        "name_selector": "h2, h3, span",
        "image_selector": "img",
        "link_selector": "a",
        "needs_js": False,
        "social": ["https://www.facebook.com/KyknosTomato/"],
    },
    "Lecker": {
        "urls": [],  # Site in maintenance mode
        "product_selector": None,
        "name_selector": None,
        "image_selector": None,
        "link_selector": None,
        "needs_js": False,
        "status": "maintenance",
        "social": [],
    },
    "Maggi": {
        "urls": ["https://www.maggicooking.gr/proionta/"],
        "product_selector": ".grid-x .cell a[href*='/product/']",
        "name_selector": "span, h3",
        "image_selector": "img[src*='search_result']",
        "link_selector": "a",
        "needs_js": True,
        "social": ["https://www.facebook.com/MaggiGreece/"],
    },
    "Paltsidis": {
        "urls": [
            "https://www.paltsidis.gr/product-category/dips/",
            "https://www.paltsidis.gr/product-category/sauces/",
        ],
        "product_selector": "li.product, .product-item",
        "name_selector": ".woocommerce-loop-product__title, h2",
        "image_selector": "img.attachment-woocommerce_thumbnail",
        "link_selector": "a.woocommerce-LoopProduct-link",
        "needs_js": False,
        "social": ["https://www.facebook.com/paltsidis.gr/"],
    },
    "Piccanta": {
        "urls": [
            "https://piccanta.gr/prod_cat/magioneza/",
            "https://piccanta.gr/prod_cat/ketsap-mustarda/",
            "https://piccanta.gr/prod_cat/sauces-dips/",
            "https://piccanta.gr/prod_cat/dressings/",
            "https://piccanta.gr/prod_cat/salates/",
        ],
        "product_selector": ".elementor-post, article",
        "name_selector": "h2, h3, .elementor-heading-title",
        "image_selector": "img",
        "link_selector": "a",
        "needs_js": True,
        "social": ["https://www.facebook.com/Piccanta/"],
    },
    "Provil": {
        "urls": [
            "https://provil.gr/",  # Homepage has new products carousel
        ],
        "product_selector": ".jet-listing-grid__item",
        "name_selector": "h2, h3, .elementor-heading-title",
        "image_selector": "img",
        "link_selector": "a",
        "needs_js": True,
        "social": ["https://www.facebook.com/ProvilGreece/"],
    },
    "Rodina": {
        "urls": [],  # No website
        "product_selector": None,
        "name_selector": None,
        "image_selector": None,
        "link_selector": None,
        "needs_js": False,
        "status": "no_website",
        "social": ["https://www.facebook.com/p/Rodina-100079499079169/"],
    },
    "Salsus": {
        "urls": ["https://www.salsus.no/en/products/"],
        "product_selector": "a[href*='/products/']",
        "name_selector": "h2, h3, span",
        "image_selector": "img",
        "link_selector": "a",
        "needs_js": False,
        "social": ["https://www.facebook.com/people/Salsus-Professionnel/61573449656994/"],
    },
    "Elvis": {
        "urls": [
            "https://elvis.com.gr/mayonnaise/",
            "https://elvis.com.gr/sauce/",
            "https://elvis.com.gr/tzatziki-2/",
            "https://elvis.com.gr/russian-salad/",
            "https://elvis.com.gr/ketchup/",
            "https://elvis.com.gr/mustard/",
        ],
        "product_selector": ".jet-listing-grid__item, article, .elementor-widget-container",
        "name_selector": "h1, h2, h3, .elementor-heading-title",
        "image_selector": "img",
        "link_selector": "a",
        "needs_js": True,
        "social": ["https://www.facebook.com/elvis.salads/"],
    },
}

# Database path
DB_PATH = "products.db"

# Scrape interval (days)
SCRAPE_INTERVAL = 15

# Request settings
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # seconds between requests
