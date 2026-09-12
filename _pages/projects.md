---
layout: default
title: Andrew Peene - Portfolio
permalink: /projects/
---

<div class="gallery-container">
<div class="project-gallery">
    {% for project in site.projects %}
      <div class="gallery-item">
        <a href="{{ project.url | relative_url }}">
          {% assign gallery_image = project.gallery_image | default: project.image %}
          {% assign gallery_imagealt = project.gallery_imagealt | default: project.title %}
          <img src="{{ gallery_image | relative_url }}" alt="{{ gallery_imagealt }}"{% if project.gallery_image_fit == "contain" %} class="gallery-image--contain"{% endif %} />
          <p>{{ project.title}}</p>
        </a>
      </div>
    {% endfor %}
</div>
</div>
