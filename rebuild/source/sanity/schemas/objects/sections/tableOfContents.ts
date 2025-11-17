import { defineType } from 'sanity'

export default defineType({
  name: 'tableOfContentsSection',
  title: 'Table of Contents Section',
  type: 'object',
  fields: [
    {
      name: 'heading',
      title: 'Heading',
      type: 'string',
      validation: (Rule) => Rule.max(100),
      initialValue: 'Table of Contents',
    },
    {
      name: 'items',
      title: 'Table of Contents Items',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'title',
              title: 'Title',
              type: 'string',
              validation: (Rule) => Rule.required().max(150),
            },
            {
              name: 'anchor',
              title: 'Anchor ID',
              type: 'string',
              description: 'HTML anchor ID to link to (e.g., "section-1")',
              validation: (Rule) => Rule.required().regex(/^[a-zA-Z0-9_-]+$/, {
                name: 'anchor ID',
                invert: false,
              }),
            },
            {
              name: 'level',
              title: 'Heading Level',
              type: 'number',
              description: 'Indentation level (1-6)',
              validation: (Rule) => Rule.required().min(1).max(6),
              initialValue: 1,
            },
          ],
          preview: {
            select: {
              title: 'title',
              level: 'level',
            },
            prepare({ title, level }) {
              const indent = '  '.repeat((level || 1) - 1)
              return {
                title: `${indent}${title}`,
                subtitle: `Level ${level}`,
              }
            },
          },
        },
      ],
      validation: (Rule) => Rule.min(1),
    },
    {
      name: 'sticky',
      title: 'Sticky Navigation',
      type: 'boolean',
      description: 'Keep table of contents visible while scrolling',
      initialValue: true,
    },
    {
      name: 'collapsible',
      title: 'Collapsible',
      type: 'boolean',
      description: 'Allow users to expand/collapse sections',
      initialValue: false,
    },
  ],
  preview: {
    select: {
      title: 'heading',
      itemCount: 'items',
    },
    prepare({ title, itemCount }) {
      return {
        title: title || 'Table of Contents',
        subtitle: itemCount ? `${itemCount.length} items` : 'No items',
      }
    },
  },
})
