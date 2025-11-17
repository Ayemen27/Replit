import { defineType } from 'sanity'

export default defineType({
  name: 'customImage',
  title: 'Image',
  type: 'image',
  options: {
    hotspot: true,
  },
  fields: [
    {
      name: 'alt',
      type: 'string',
      title: 'Alternative Text',
      description: 'Important for SEO and accessibility',
      validation: (Rule) => Rule.required(),
    },
    {
      name: 'caption',
      type: 'string',
      title: 'Caption',
      description: 'Optional caption displayed below the image',
    },
    {
      name: 'attribution',
      type: 'string',
      title: 'Attribution',
      description: 'Photo credit or source',
    },
  ],
  preview: {
    select: {
      media: 'asset',
      alt: 'alt',
      caption: 'caption',
    },
    prepare({ media, alt, caption }) {
      return {
        title: alt || 'Image',
        subtitle: caption,
        media,
      }
    },
  },
})
