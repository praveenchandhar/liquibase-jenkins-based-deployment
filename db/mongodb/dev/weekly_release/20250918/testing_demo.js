// context: liquibase_test

// Insert test users
db.users.insertMany([
    {
        name: "John Doe",
        email: "john@example.com",
        role: "admin",
        created: new Date(),
        status: "active"
    },
    {
        name: "Jane Smith",
        email: "jane@example.com", 
        role: "user",
        created: new Date(),
        status: "active"
    }
]);

// Create index on email
db.users.createIndex({ email: 1 }, { unique: true });

// Insert test order
db.orders.insertOne({
    userId: "john@example.com",
    items: ["laptop", "mouse"],
    total: 1029.99,
    status: "pending",
    created: new Date()
});
