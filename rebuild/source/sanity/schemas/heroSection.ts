import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'heroSection',
  title: 'Hero Section',
  type: 'document',
  fields: [
    defineField({
      name: 'key',
      title: 'Key',
      type: 'string',
      description: 'Unique identifier for this hero section (e.g., "home", "gallery", "pricing")',
      validation: (Rule) =>
        Rule.required()
          .max(50)
          .regex(/^[a-z0-9-]+$/, {
            name: 'slug format',
            invert: false,
          })
          .error('Key must be lowercase letters, numbers, and hyphens only'),
    }),
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required().max(150),
    }),
    defineField({
      name: 'subtitle',
      title: 'Subtitle',
      type: 'string',
      validation: (Rule) => Rule.max(200),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 4,
      validation: (Rule) => Rule.max(500),
    }),
    defineField({
      name: 'ctaText',
      title: 'CTA Text',
      type: 'string',
      description: 'Call-to-action button text',
      validation: (Rule) => Rule.max(50),
    }),
    defineField({
      name: 'ctaUrl',
      title: 'CTA URL',
      type: 'url',
      description: 'Call-to-action button URL',
      validation: (Rule) =>
        Rule.uri({
          scheme: ['http', 'https', '/'],
          allowRelative: true,
        }),
    }),
    defineField({
      name: 'backgroundImage',
      title: 'Background Image',
      type: 'image',
      options: {
        hotspot: true,
      },
      fields: [
        {
          name: 'alt',
          type: 'string',
          title: 'Alternative Text',
        },
      ],
    }),
    defineField({
      name: 'backgroundVideo',
      title: 'Background Video URL',
      type: 'url',
      description: 'Video URL for background (optional, overrides image)',
      validation: (Rule) =>
        Rule.uri({
          scheme: ['http', 'https'],
        }),
    }),
    defineField({
      name: 'isActive',
      title: 'Is Active',
      type: 'boolean',
      description: 'Set to true to display this hero section',
      initialValue: true,
    }),
  ],
  preview: {
    select: {
      title: 'title',
      subtitle: 'key',
      media: 'backgroundImage',
      isActive: 'isActive',
    },
    prepare({ title, subtitle, media, isActive }) {
      return {
        title,
        subtitle: `${subtitle} ${isActive ? '✓' : '(Inactive)'}`,
        media,
      }
    },
  },
})
