import { defineType } from 'sanity'

export default defineType({
  name: 'button',
  title: 'Button',
  type: 'object',
  fields: [
    {
      name: 'text',
      title: 'Button Text',
      type: 'string',
      validation: (Rule) => Rule.required().max(50),
    },
    {
      name: 'link',
      title: 'Link',
      type: 'link',
    },
    {
      name: 'style',
      title: 'Button Style',
      type: 'string',
      options: {
        list: [
          { title: 'Primary', value: 'primary' },
          { title: 'Secondary', value: 'secondary' },
          { title: 'Outline', value: 'outline' },
          { title: 'Ghost', value: 'ghost' },
          { title: 'Link', value: 'link' },
        ],
        layout: 'dropdown',
      },
      initialValue: 'primary',
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
    {
      name: 'icon',
      title: 'Icon',
      type: 'string',
      description: 'Icon name or class (optional)',
    },
    {
      name: 'iconPosition',
      title: 'Icon Position',
      type: 'string',
      options: {
        list: [
          { title: 'Left', value: 'left' },
          { title: 'Right', value: 'right' },
        ],
        layout: 'radio',
      },
      initialValue: 'right',
      hidden: ({ parent }) => !parent?.icon,
    },
  ],
  preview: {
    select: {
      text: 'text',
      style: 'style',
    },
    prepare({ text, style }) {
      return {
        title: text || 'Button',
        subtitle: `Style: ${style || 'primary'}`,
      }
    },
  },
})
