-- Reason counts overlap: one physical record can have several reasons.
SELECT r.publication_id, r.batch_id, r.entity, reason,
       count(DISTINCT r.occurrence_id) AS rejected_records
FROM rejected_records_snapshots r
JOIN publication p ON array_contains(p.publication_ids, r.publication_id)
LATERAL VIEW explode(r.reasons) reasons AS reason
WHERE r.publication_id = :publication_id AND NOT r.resolved
GROUP BY r.publication_id, r.batch_id, r.entity, reason
ORDER BY rejected_records DESC, reason
