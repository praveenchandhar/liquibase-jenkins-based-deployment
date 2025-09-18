// context: liquibase_test

// Insert test order
db.orders.insertOne({
    userId: "john@example.com",
    items: ["laptop", "mouse"],
    total: 1029.99,
    status: "pending",
    created: new Date()
});
