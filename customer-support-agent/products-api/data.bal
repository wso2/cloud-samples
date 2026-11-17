// Mock catalog for a fictional outdoor gear store. Held in memory because the filesystem is read-only.

final readonly & map<Product> products = {
    "JKT-TRAIL-01": {
        sku: "JKT-TRAIL-01",
        name: "Trailblazer Rain Jacket",
        category: "jackets",
        price: 129.00,
        currency: "USD",
        description: "Lightweight waterproof shell for wet hikes and windy ridges.",
        features: ["Waterproof 20,000 mm membrane", "Pit zips", "Packs into its own pocket", "Weight 310 g"],
        sizes: ["S", "M", "L", "XL"],
        rating: 4.6
    },
    "JKT-FLEECE-02": {
        sku: "JKT-FLEECE-02",
        name: "Ridge Fleece Jacket",
        category: "jackets",
        price: 79.00,
        currency: "USD",
        description: "Warm mid-layer fleece for cold mornings in camp.",
        features: ["Recycled polyester fleece", "Two zip hand pockets", "Weight 420 g"],
        sizes: ["S", "M", "L", "XL"],
        rating: 4.4
    },
    "TNT-SUMMIT-2": {
        sku: "TNT-SUMMIT-2",
        name: "Summit 2 Tent",
        category: "tents",
        price: 249.00,
        currency: "USD",
        description: "Two-person, three-season backpacking tent.",
        features: ["Sleeps 2", "Packed weight 1.6 kg", "One door, one vestibule", "Floor area 2.7 m2"],
        sizes: ["ONE"],
        rating: 4.5
    },
    "TNT-SUMMIT-3": {
        sku: "TNT-SUMMIT-3",
        name: "Summit 3 Tent",
        category: "tents",
        price: 329.00,
        currency: "USD",
        description: "Three-person, three-season tent with two doors.",
        features: ["Sleeps 3", "Packed weight 2.2 kg", "Two doors, two vestibules", "Floor area 3.9 m2"],
        sizes: ["ONE"],
        rating: 4.7
    },
    "BAG-NORTH-20": {
        sku: "BAG-NORTH-20",
        name: "Northwind 20F Sleeping Bag",
        category: "sleeping-bags",
        price: 189.00,
        currency: "USD",
        description: "Down sleeping bag rated to 20F (-7C).",
        features: ["650-fill down", "Comfort rating 28F (-2C)", "Weight 1.1 kg"],
        sizes: ["REGULAR", "LONG"],
        rating: 4.3
    },
    "PCK-CREST-40": {
        sku: "PCK-CREST-40",
        name: "Crest 40L Backpack",
        category: "packs",
        price: 149.00,
        currency: "USD",
        description: "40 litre pack for overnight trips.",
        features: ["Adjustable torso", "Hip-belt pockets", "Rain cover included"],
        sizes: ["S-M", "M-L"],
        rating: 4.5
    },
    "BTS-ASCENT-01": {
        sku: "BTS-ASCENT-01",
        name: "Ascent Hiking Boots",
        category: "footwear",
        price: 159.00,
        currency: "USD",
        description: "Waterproof mid-cut boots for rocky trails.",
        features: ["Waterproof leather", "Vibram sole", "Weight 1.2 kg per pair"],
        sizes: ["7", "8", "9", "10", "11"],
        rating: 4.2
    },
    "STV-PEAK-01": {
        sku: "STV-PEAK-01",
        name: "Peak Camp Stove",
        category: "cooking",
        price: 59.00,
        currency: "USD",
        description: "Compact canister stove that boils a litre in about 3.5 minutes.",
        features: ["Piezo igniter", "Weight 85 g", "Fits standard screw-on canisters"],
        sizes: ["ONE"],
        rating: 4.8
    }
};

// Units on hand per size. Read-only: the API has no write routes.
final readonly & map<map<int>> stockLevels = {
    "JKT-TRAIL-01": {"S": 4, "M": 0, "L": 7, "XL": 2},
    "JKT-FLEECE-02": {"S": 10, "M": 12, "L": 8, "XL": 0},
    "TNT-SUMMIT-2": {"ONE": 5},
    "TNT-SUMMIT-3": {"ONE": 0},
    "BAG-NORTH-20": {"REGULAR": 6, "LONG": 1},
    "PCK-CREST-40": {"S-M": 3, "M-L": 9},
    "BTS-ASCENT-01": {"7": 2, "8": 5, "9": 0, "10": 4, "11": 1},
    "STV-PEAK-01": {"ONE": 25}
};

final readonly & map<Policy> policies = {
    "returns": {
        topic: "returns",
        title: "Returns",
        summary: "Return unused items within 30 days for a full refund.",
        details: [
            "Items must be unused, with tags, and come with the receipt or order number.",
            "Footwear worn outdoors can be returned within 60 days only for a manufacturing defect.",
            "Refunds go back to the original payment method within 5 business days."
        ]
    },
    "shipping": {
        topic: "shipping",
        title: "Shipping",
        summary: "Free standard shipping on orders over USD 75.",
        details: [
            "Standard shipping takes 3 to 5 business days and costs USD 6 below USD 75.",
            "Express shipping takes 1 to 2 business days and costs USD 18.",
            "Orders placed before 2 pm ship the same business day."
        ]
    },
    "warranty": {
        topic: "warranty",
        title: "Warranty",
        summary: "Two years on tents and packs, one year on everything else.",
        details: [
            "The warranty covers manufacturing defects, not wear and tear or accidental damage.",
            "Bring the item to a store or start a claim with the order number."
        ]
    },
    "price-match": {
        topic: "price-match",
        title: "Price match",
        summary: "We match a lower price from an authorised retailer within 14 days of purchase.",
        details: [
            "The item must be identical and in stock at the other retailer.",
            "Clearance, auction and membership-only prices are not matched."
        ]
    }
};
