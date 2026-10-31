-- Bind publication_id once for every dataset on the dashboard.
SELECT f.publication_id, f.order_id, f.line_id, f.order_date, f.sale_region,
       f.customer_id, f.product_id, d.product_name, d.category,
       concat(f.product_id, ' / ', d.product_name) AS product_label,
       f.quantity, f.unit_price, f.discount_amount, f.net_sales,
       f.snapshot_created_at
FROM fact_order_line_snapshots f
JOIN dim_product_snapshots d
  ON f.product_id = d.product_id AND f.publication_id = d.publication_id
JOIN publication p ON array_contains(p.publication_ids, f.publication_id)
WHERE f.publication_id = :publication_id
