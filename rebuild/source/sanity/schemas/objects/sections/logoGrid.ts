import { defineType } from 'sanity'

export default defineType({
  name: 'logoGridSection',
  title: 'Logo Grid Section',
  type: 'object',
  fields: [
    {
      name: 'heading',
      title: 'Heading',
      type: 'string',
      validation: (Rule) => Rule.max(150),
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 3,
    },
    {
      name: 'logos',
      title: 'Logos',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'image',
              title: 'Logo Image',
              type: 'customImage',
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'alt',
              title: 'Alt Text',
              type: 'string',
              description: 'Alternative text for the logo',
              validation: (Rule) => Rule.required().max(100),
            },
            {
              name: 'link',
              title: 'Link',
              type: 'url',
              description: 'Optional link when clicking the logo',
            },
          ],
          preview: {
            select: {
              alt: 'alt',
              media: 'image',
            },
            prepare({ alt, media }) {
              return {
                title: alt || 'Logo',
                media,
              }
            },
          },
        },
      ],
      validation: (Rule) => Rule.min(1),
    },
    {
      name: 'columns',
      title: 'Columns',
      type: 'string',
      options: {
        list: [
          { title: '2 Columns', value: '2' },
          { title: '3 Columns', value: '3' },
          { title: '4 Columns', value: '4' },
          { title: '5 Columns', value: '5' },
          { title: '6 Columns', value: '6' },
        ],
        layout: 'dropdown',
      },
      initialValue: '4',
    },
    {
      name: 'grayscale',
      title: 'Grayscale',
      type: 'boolean',
      description: 'Display logos in grayscale (with color on hover)',
      initialValue: false,
    },
  ],
  preview: {
    select: {
      title: 'heading',
      logoCount: 'logos',
    },
    prepare({ title, logoCount }) {
      return {
        title: title || 'Logo Grid Section',
        subtitle: logoCount ? `${logoCount.length} logos` : 'No logos',
      }
    },
  },
})
