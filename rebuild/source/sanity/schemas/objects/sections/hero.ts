import { defineType } from 'sanity'

export default defineType({
  name: 'heroSection',
  title: 'Hero Section',
  type: 'object',
  fields: [
    {
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required().max(100),
    },
    {
      name: 'subtitle',
      title: 'Subtitle',
      type: 'string',
      validation: (Rule) => Rule.max(150),
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 3,
      validation: (Rule) => Rule.max(300),
    },
    {
      name: 'buttons',
      title: 'CTA Buttons',
      type: 'array',
      of: [{ type: 'button' }],
      validation: (Rule) => Rule.max(3),
    },
    {
      name: 'backgroundImage',
      title: 'Background Image',
      type: 'customImage',
    },
    {
      name: 'backgroundVideo',
      title: 'Background Video URL',
      type: 'url',
      description: 'URL to video file (MP4, WebM)',
    },
    {
      name: 'alignment',
      title: 'Text Alignment',
      type: 'string',
      options: {
        list: [
          { title: 'Left', value: 'left' },
          { title: 'Center', value: 'center' },
          { title: 'Right', value: 'right' },
        ],
        layout: 'radio',
      },
      initialValue: 'center',
    },
    {
      name: 'overlay',
      title: 'Overlay',
      type: 'object',
      fields: [
        {
          name: 'enabled',
          title: 'Enable Overlay',
          type: 'boolean',
          initialValue: false,
        },
        {
          name: 'opacity',
          title: 'Opacity',
          type: 'number',
          validation: (Rule) => Rule.min(0).max(1),
          initialValue: 0.5,
          hidden: ({ parent }) => !parent?.enabled,
        },
      ],
    },
  ],
  preview: {
    select: {
      title: 'title',
      subtitle: 'subtitle',
      media: 'backgroundImage',
    },
  },
})
