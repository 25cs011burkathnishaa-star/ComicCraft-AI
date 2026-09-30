def build_comic_layout(image_paths, full_story, outline):
    """
    Organizes the generated images and full comic story into a structured layout.
    """
    story_panels = full_story.split("**Panel")
    story_panels = [f"**Panel{panel}" for panel in story_panels if panel.strip()]
    
    if not story_panels:
        story_panels = [full_story] * len(outline)

    layout = []
    for idx, (image, panel_info) in enumerate(zip(image_paths, outline), start=1):
        text_content = story_panels[idx-1] if idx-1 < len(story_panels) else panel_info.get("scene_description", "")
        
        lines = text_content.strip().splitlines()
        cleaned_lines = [line for line in lines if not line.strip().lower().startswith("**panel")]
        cleaned_text = "\n".join(cleaned_lines).strip()
        if not cleaned_text:
            cleaned_text = panel_info.get("scene_description", "")

        layout.append({
            "panel": idx,
            "title": panel_info.get("title", f"Panel {idx}"),
            "image_path": image,
            "text": cleaned_text,
            "scene_description": panel_info.get("scene_description", "")
        })
    return layout