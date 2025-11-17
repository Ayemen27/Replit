import { defineType } from 'sanity'

export default defineType({
  name: 'alternatingEditorialSection',
  title: 'Alternating Editorial Section',
  type: 'object',
  fields: [
    {
      name: 'heading',
      title: 'Section Heading',
      type: 'string',
      validation: (Rule) => Rule.max(150),
    },
    {
      name: 'items',
      title: 'Content Items',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'title',
              title: 'Title',
              type: 'string',
              validation: (Rule) => Rule.required().max(100),
            },
            {
              name: 'content',
              title: 'Content',
              type: 'richText',
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'image',
              title: 'Image',
              type: 'customImage',
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'imagePosition',
              title: 'Image Position',
              type: 'string',
              options: {
                list: [
                  { title: 'Left', value: 'left' },
                  { title: 'Right', value: 'right' },
                ],
                layout: 'radio',
              },
              initialValue: 'right',
              description: 'Will alternate automatically if not specified',
            },
            {
              name: 'buttons',
              title: 'Buttons',
              type: 'array',
              of: [{ type: 'button' }],
              validation: (Rule) => Rule.max(2),
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
      validation: (Rule) => Rule.min(1).max(10),
    },
  ],
  preview: {
    select: {
      title: 'heading',
      itemCount: 'items',
    },
    prepare({ title, itemCount }) {
      return {
        title: title || 'Alternating Editorial',
        subtitle: itemCount ? `${itemCount.length} items` : 'No items',
      }
    },
  },
})
