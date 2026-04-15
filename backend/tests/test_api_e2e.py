from io import BytesIO


def test_upload_classify_filter_and_annotate_flow(client) -> None:
    upload_response = client.post(
        "/v1/library/upload",
        files={"file": ("tokyo_runway_jacket.jpg", BytesIO(b"fake-image"), "image/jpeg")},
        data={
            "designer_tags": "runway,outerwear",
            "designer_notes": "Initial note",
        },
    )

    assert upload_response.status_code == 200
    item = upload_response.json()["item"]
    item_id = item["id"]

    filter_response = client.get("/v1/library", params={"country": "Japan", "garment_type": "Jacket"})
    assert filter_response.status_code == 200
    assert len(filter_response.json()["items"]) >= 1

    annotate_response = client.patch(
        f"/v1/library/{item_id}/annotations",
        json={"designer_tags": ["updated", "runway"], "designer_notes": "Updated note"},
    )
    assert annotate_response.status_code == 200
    updated = annotate_response.json()["item"]
    assert updated["designer_tags"] == ["updated", "runway"]
    assert updated["designer_notes"] == "Updated note"
