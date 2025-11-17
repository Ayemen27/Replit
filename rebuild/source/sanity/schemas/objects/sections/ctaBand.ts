import { defineType } from 'sanity'

export default defineType({
  name: 'ctaBandSection',
  title: 'CTA Band',
  type: 'object',
  fields: [
    {
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required().max(150),
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
      title: 'Buttons',
      type: 'array',
      of: [{ type: 'button' }],
      validation: (Rule) => Rule.min(1).max(3),
    },
    {
      name: 'alignment',
      title: 'Alignment',
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
      name: 'backgroundColor',
      title: 'Background Color',
      type: 'string',
      options: {
        list: [
          { title: 'Default', value: 'default' },
          { title: 'Primary', value: 'primary' },
          { title: 'Secondary', value: 'secondary' },
          { title: 'Accent', value: 'accent' },
          { title: 'Gradient', value: 'gradient' },
        ],
      },
      initialValue: 'primary',
    },
    {
      name: 'backgroundImage',
      title: 'Background Image',
      type: 'customImage',
      description: 'Optional background image',
    },
    {
      name: 'size',
      title: 'Size',
      type: 'string',
      options: {
        list: [
          { title: 'Small', value: 'sm' },
          { title: 'Medium', value: 'md' },
          { title: 'Large', value: 'lg' },
        ],
        layout: 'radio',
      },
      initialValue: 'md',
    },
  ],
  preview: {
    select: {
      title: 'title',
      media: 'backgroundImage',
    },
  },
})
