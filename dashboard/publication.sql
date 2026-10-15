SELECT publication_id AS latest_publication_id, published_at AS latest_published_at,
       explode(publication_ids) AS available_publication_id
FROM publication
