import ballerina/http;

configurable int port = 8080;

// A read-only catalog API with no auth code. It runs in the same project as the MCP server and is
// reachable only from inside the project, so it needs none.
service /api/v1 on new http:Listener(port) {

    resource function get health() returns map<string> {
        return {status: "ok"};
    }

    # Search the catalog by a word in the name, description or category.
    #
    # + query - Text to look for, case-insensitive; empty returns everything
    # + category - Optional category such as "tents"
    # + return - Matching products, best rated first
    resource function get products(string query = "", string category = "") returns ProductSummary[] {
        string q = query.trim().toLowerAscii();
        string c = category.trim().toLowerAscii();
        return from Product p in products
            where (c == "" || p.category == c)
                && (q == "" || p.name.toLowerAscii().includes(q)
                    || p.description.toLowerAscii().includes(q)
                    || p.category.includes(q))
            order by p.rating descending
            select {sku: p.sku, name: p.name, category: p.category, price: p.price, currency: p.currency};
    }

    resource function get products/[string sku]() returns Product|http:NotFound {
        Product? p = products[sku];
        return p is () ? http:NOT_FOUND : p;
    }

    resource function get products/[string sku]/stock() returns Stock|http:NotFound {
        Stock? stock = stockFor(sku);
        return stock is () ? http:NOT_FOUND : stock;
    }

    resource function get policies() returns PolicySummary[] {
        return from Policy p in policies
            select {topic: p.topic, title: p.title};
    }

    resource function get policies/[string topic]() returns Policy|http:NotFound {
        Policy? p = policies[topic];
        return p is () ? http:NOT_FOUND : p;
    }
}

isolated function stockFor(string sku) returns Stock? {
    map<int>? levels = stockLevels[sku];
    if levels is () {
        return ();
    }
    SizeStock[] sizes = [];
    boolean inStock = false;
    foreach [string, int] [size, quantity] in levels.entries() {
        sizes.push({size, quantity});
        if quantity > 0 {
            inStock = true;
        }
    }
    return {sku, inStock, sizes};
}
