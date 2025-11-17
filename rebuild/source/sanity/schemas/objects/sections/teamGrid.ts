import { defineType } from 'sanity'

export default defineType({
  name: 'teamGridSection',
  title: 'Team Grid Section',
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
      validation: (Rule) => Rule.max(300),
    },
    {
      name: 'members',
      title: 'Team Members',
      type: 'array',
      of: [{ type: 'person' }],
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
        ],
        layout: 'radio',
      },
      initialValue: '3',
    },
    {
      name: 'showBio',
      title: 'Show Bio',
      type: 'boolean',
      description: 'Display member bio text',
      initialValue: true,
    },
  ],
  preview: {
    select: {
      title: 'heading',
      memberCount: 'members',
    },
    prepare({ title, memberCount }) {
      return {
        title: title || 'Team Grid Section',
        subtitle: memberCount ? `${memberCount.length} team members` : 'No members',
      }
    },
  },
})
