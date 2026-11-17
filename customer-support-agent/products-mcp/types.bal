// Mirrors the Products API's response shapes.

type Product record {|
    string sku;
    string name;
    string category;
    decimal price;
    string currency;
    string description;
    string[] features;
    string[] sizes;
    decimal rating;
|};

type ProductSummary record {|
    string sku;
    string name;
    string category;
    decimal price;
    string currency;
|};

type SizeStock record {|
    string size;
    int quantity;
|};

type Stock record {|
    string sku;
    boolean inStock;
    SizeStock[] sizes;
|};

type Policy record {|
    string topic;
    string title;
    string summary;
    string[] details;
|};
