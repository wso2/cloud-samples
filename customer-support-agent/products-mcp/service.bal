import ballerina/http;
import ballerina/lang.regexp;
import ballerina/log;
import ballerina/mcp;

configurable int port = 9090;

final regexp:RegExp skuPattern = re `[A-Z0-9-]{3,32}`;
final regexp:RegExp topicPattern = re `[a-z-]{1,32}`;

listener mcp:StreamableHttpListener productsListener = check new (port);

// Stateless, so any replica can answer any request. Read-only: four tools that look things up.
@mcp:StreamableHttpServiceConfig {
    info: {
        name: "Products MCP Server",
        version: "0.1.0"
    },
    sessionMode: mcp:STATELESS,
    options: {
        instructions: "Product catalog, stock and store policies for Summit Outdoor."
    }
}
service mcp:StreamableHttpService /mcp on productsListener {

    # Search the product catalog by name, description or category.
    #
    # + query - Words to look for, such as "rain jacket" or "tent"
    # + category - Optional category: jackets, tents, sleeping-bags, packs, footwear or cooking
    # + return - Matching products with SKU and price, best rated first
    remote function searchProducts(string query, string? category = ()) returns ProductSummary[]|error {
        string q = query.trim();
        if q.length() > 100 {
            return error("Keep the search under 100 characters");
        }
        ProductSummary[]|http:ClientError products =
            productsApi->/products(query = q, category = (category ?: "").trim());
        return products is http:ClientError ? apiError(products, "No products matched") : products;
    }

    # Get the full details of one product: description, features, sizes, price and rating.
    #
    # + sku - The product SKU such as "JKT-TRAIL-01", from searchProducts
    # + return - The product, or an error if no product has that SKU
    remote function getProduct(string sku) returns Product|error {
        string id = check normalizeSku(sku);
        Product|http:ClientError product = productsApi->/products/[id]();
        return product is http:ClientError ? apiError(product, string `No product with SKU ${id}`) : product;
    }

    # Check how many units are in stock for each size of a product.
    #
    # + sku - The product SKU such as "JKT-TRAIL-01", from searchProducts
    # + return - Units on hand per size, and whether any size is in stock
    remote function checkStock(string sku) returns Stock|error {
        string id = check normalizeSku(sku);
        Stock|http:ClientError stock = productsApi->/products/[id]/stock();
        return stock is http:ClientError ? apiError(stock, string `No product with SKU ${id}`) : stock;
    }

    # Read a store policy.
    #
    # + topic - One of: returns, shipping, warranty, price-match
    # + return - The policy summary and its details
    remote function getPolicy(string topic) returns Policy|error {
        string t = topic.trim().toLowerAscii();
        string unknown = "Unknown policy. Topics are: returns, shipping, warranty, price-match";
        if !topicPattern.isFullMatch(t) {
            return error(unknown);
        }
        Policy|http:ClientError policy = productsApi->/policies/[t]();
        return policy is http:ClientError ? apiError(policy, unknown) : policy;
    }
}

// Accepts "jkt-trail-01" or " JKT-TRAIL-01 " and rejects anything that isn't a SKU.
isolated function normalizeSku(string sku) returns string|error {
    string id = sku.trim().toUpperAscii();
    if !skuPattern.isFullMatch(id) {
        return error("SKUs look like JKT-TRAIL-01. Use searchProducts to find one");
    }
    return id;
}

// Only a 404 means "not found". Other failures get their own message, so a broken setup isn't
// reported to shoppers as a missing product.
isolated function apiError(http:ClientError err, string notFound) returns error {
    if err is http:ClientRequestError {
        int status = err.detail().statusCode;
        if status == 404 {
            return error(notFound);
        }
        log:printError("Products API rejected the request", 'error = err, statusCode = status);
        return error("The product catalog rejected this request");
    }
    log:printError("Products API call failed", 'error = err);
    return error("The product catalog is unavailable right now");
}
