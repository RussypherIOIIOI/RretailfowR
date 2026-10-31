SELECT r.publication_id, r.occurrence_id, r.batch_id, r.entity, r.filename,
       r.record_index, r.raw_record, r.business_key, r.source_revision,
       r.disposition, r.reasons, r.resolved, r.ruleset,
       CASE WHEN NOT r.resolved THEN r.occurrence_id END AS unresolved_occurrence_id,
       CASE WHEN r.resolved THEN r.occurrence_id END AS resolved_occurrence_id,
       r.first_rejected_at, r.last_rejected_at, r.evaluated_at
FROM rejected_records_snapshots r
JOIN publication p ON array_contains(p.publication_ids, r.publication_id)
WHERE r.publication_id = :publication_id
