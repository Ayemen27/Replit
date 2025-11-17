import { defineType } from 'sanity'

export default defineType({
  name: 'standardTextSection',
  title: 'Standard Text Section',
  type: 'object',
  fields: [
    {
      name: 'heading',
      title: 'Heading',
      type: 'string',
      validation: (Rule) => Rule.max(150),
    },
    {
      name: 'content',
      title: 'Content',
      type: 'richText',
      validation: (Rule) => Rule.required(),
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
      initialValue: 'left',
    },
    {
      name: 'maxWidth',
      title: 'Max Width',
      type: 'string',
      options: {
        list: [
          { title: 'Small', value: 'sm' },
          { title: 'Medium', value: 'md' },
          { title: 'Large', value: 'lg' },
          { title: 'Full', value: 'full' },
        ],
        layout: 'radio',
      },
      initialValue: 'md',
    },
  ],
  preview: {
    select: {
      title: 'heading',
    },
    prepare({ title }) {
      return {
        title: title || 'Standard Text Section',
        subtitle: 'Text content',
      }
    },
  },
})
