import assert from 'node:assert/strict'
import test from 'node:test'

import { parseMetadataResponse } from './metadata.ts'

test('unwraps available plan metadata from the API response', () => {
  const result = parseMetadataResponse({
    plan_id: 'SP_U1_0002',
    exists: true,
    metadata: {
      image_width_px: 18896,
      image_height_px: 13364,
      scale_text_visible: 'M1:50',
      source_type: 'rendered_png',
    },
    warnings: [],
    errors: [],
  })

  assert.equal(result.kind, 'available')
  if (result.kind === 'available') {
    assert.equal(result.metadata.image_width_px, 18896)
    assert.equal(result.metadata.scale_text_visible, 'M1:50')
  }
})

test('preserves the backend warning when metadata is missing', () => {
  const result = parseMetadataResponse({
    exists: false,
    metadata: {},
    warnings: ['metadata file not found'],
    errors: [],
  })

  assert.deepEqual(result, {
    kind: 'missing',
    message: 'metadata file not found',
  })
})

test('preserves the backend error when metadata is malformed', () => {
  const result = parseMetadataResponse({
    exists: false,
    metadata: {},
    warnings: [],
    errors: ['failed to read metadata file: invalid JSON'],
  })

  assert.deepEqual(result, {
    kind: 'error',
    message: 'failed to read metadata file: invalid JSON',
  })
})
