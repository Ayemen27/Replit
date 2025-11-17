import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'siteSettings',
  title: 'Site Settings',
  type: 'document',
  fields: [
    defineField({
      name: 'siteName',
      title: 'Site Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'logo',
      title: 'Logo',
      type: 'image',
      options: {
        hotspot: true,
      },
      fields: [
        {
          name: 'alt',
          type: 'string',
          title: 'Alternative Text',
          validation: (Rule) => Rule.required(),
        },
      ],
    }),
    defineField({
      name: 'favicon',
      title: 'Favicon',
      type: 'image',
      description: 'Favicon for the site (32x32px recommended)',
    }),
    defineField({
      name: 'colors',
      title: 'Brand Colors',
      type: 'object',
      fields: [
        {
          name: 'primary',
          title: 'Primary Color',
          type: 'string',
          description: 'Hex color code (e.g., #0066CC)',
          validation: (Rule) => Rule.regex(/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/, {
            name: 'hex color',
            invert: false,
          }),
        },
        {
          name: 'secondary',
          title: 'Secondary Color',
          type: 'string',
          description: 'Hex color code (e.g., #FF6600)',
          validation: (Rule) => Rule.regex(/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/, {
            name: 'hex color',
            invert: false,
          }),
        },
        {
          name: 'accent',
          title: 'Accent Color',
          type: 'string',
          description: 'Hex color code (e.g., #00CC66)',
          validation: (Rule) => Rule.regex(/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/, {
            name: 'hex color',
            invert: false,
          }),
        },
      ],
      options: {
        collapsible: true,
        collapsed: false,
      },
    }),
    defineField({
      name: 'defaultSEO',
      title: 'Default SEO',
      type: 'object',
      fields: [
        {
          name: 'title',
          title: 'Default SEO Title',
          type: 'string',
          validation: (Rule) => Rule.max(60),
        },
        {
          name: 'description',
          title: 'Default SEO Description',
          type: 'text',
          rows: 3,
          validation: (Rule) => Rule.max(160),
        },
        {
          name: 'keywords',
          title: 'Default Keywords',
          type: 'array',
          of: [{ type: 'string' }],
          options: {
            layout: 'tags',
          },
        },
        {
          name: 'ogImage',
          title: 'Default Open Graph Image',
          type: 'image',
          description: 'Default image for social media sharing (1200x630px recommended)',
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
        },
      ],
      options: {
        collapsible: true,
        collapsed: false,
      },
    }),
    defineField({
      name: 'analytics',
      title: 'Analytics',
      type: 'object',
      fields: [
        {
          name: 'googleAnalyticsId',
          title: 'Google Analytics ID',
          type: 'string',
          description: 'GA4 Measurement ID (e.g., G-XXXXXXXXXX)',
        },
        {
          name: 'googleTagManagerId',
          title: 'Google Tag Manager ID',
          type: 'string',
          description: 'GTM Container ID (e.g., GTM-XXXXXXX)',
        },
      ],
      options: {
        collapsible: true,
        collapsed: true,
      },
    }),
  ],
  preview: {
    select: {
      title: 'siteName',
      media: 'logo',
    },
  },
})
