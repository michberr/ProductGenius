# Postgres code to create full-text search indexes

# Index on products
CREATE INDEX idx_fts_product ON products 
USING gin((setweight(to_tsvector('english', title), 'A') || 
           setweight(to_tsvector('english', description), 'B')));

# Index on reviews
CREATE INDEX idx_fts_review ON reviews 
USING gin((setweight(to_tsvector('english', summary), 'A') || 
           setweight(to_tsvector('english', review), 'B')));