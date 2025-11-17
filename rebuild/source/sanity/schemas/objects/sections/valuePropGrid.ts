import { defineType } from 'sanity'

export default defineType({
  name: 'valuePropGridSection',
  title: 'Value Proposition Grid',
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
      name: 'items',
      title: 'Value Propositions',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'icon',
              title: 'Icon',
              type: 'string',
              description: 'Icon name or class',
            },
            {
              name: 'image',
              title: 'Image',
              type: 'customImage',
              description: 'Use image instead of icon',
            },
            {
              name: 'title',
              title: 'Title',
              type: 'string',
              validation: (Rule) => Rule.required().max(80),
            },
            {
              name: 'description',
              title: 'Description',
              type: 'text',
              rows: 3,
              validation: (Rule) => Rule.max(250),
            },
            {
              name: 'link',
              title: 'Link',
              type: 'link',
            },
          ],
          preview: {
            select: {
              title: 'title',
              media: 'image',
            },
          },
        },
      ],
      validation: (Rule) => Rule.min(1).max(12),
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
        ],
        layout: 'radio',
      },
      initialValue: '3',
    },
  ],
  preview: {
    select: {
      title: 'heading',
      itemCount: 'items',
    },
    prepare({ title, itemCount }) {
      return {
        title: title || 'Value Proposition Grid',
        subtitle: itemCount ? `${itemCount.length} items` : 'No items',
      }
    },
  },
})
