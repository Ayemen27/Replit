import { defineType } from 'sanity'

export default defineType({
  name: 'pricingTableSection',
  title: 'Pricing Table',
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
      name: 'billingPeriod',
      title: 'Billing Period Toggle',
      type: 'object',
      fields: [
        {
          name: 'enabled',
          title: 'Enable Period Toggle',
          type: 'boolean',
          initialValue: true,
        },
        {
          name: 'periods',
          title: 'Periods',
          type: 'array',
          of: [
            {
              type: 'object',
              fields: [
                {
                  name: 'label',
                  title: 'Label',
                  type: 'string',
                  validation: (Rule) => Rule.required(),
                },
                {
                  name: 'value',
                  title: 'Value',
                  type: 'string',
                  validation: (Rule) => Rule.required(),
                },
              ],
            },
          ],
          hidden: ({ parent }) => !parent?.enabled,
        },
      ],
    },
    {
      name: 'plans',
      title: 'Pricing Plans',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'name',
              title: 'Plan Name',
              type: 'string',
              validation: (Rule) => Rule.required().max(50),
            },
            {
              name: 'description',
              title: 'Description',
              type: 'text',
              rows: 2,
              validation: (Rule) => Rule.max(200),
            },
            {
              name: 'price',
              title: 'Price',
              type: 'object',
              fields: [
                {
                  name: 'amount',
                  title: 'Amount',
                  type: 'string',
                  description: 'e.g., 0, 20, 99',
                  validation: (Rule) => Rule.required(),
                },
                {
                  name: 'currency',
                  title: 'Currency',
                  type: 'string',
                  initialValue: 'USD',
                },
                {
                  name: 'period',
                  title: 'Period',
                  type: 'string',
                  description: 'e.g., /month, /year',
                  initialValue: '/month',
                },
              ],
            },
            {
              name: 'features',
              title: 'Features',
              type: 'array',
              of: [
                {
                  type: 'object',
                  fields: [
                    {
                      name: 'text',
                      title: 'Feature Text',
                      type: 'string',
                      validation: (Rule) => Rule.required(),
                    },
                    {
                      name: 'included',
                      title: 'Included',
                      type: 'boolean',
                      initialValue: true,
                    },
                    {
                      name: 'tooltip',
                      title: 'Tooltip',
                      type: 'string',
                      description: 'Additional information',
                    },
                  ],
                  preview: {
                    select: {
                      text: 'text',
                      included: 'included',
                    },
                    prepare({ text, included }) {
                      return {
                        title: text,
                        subtitle: included ? '✓ Included' : '✗ Not included',
                      }
                    },
                  },
                },
              ],
            },
            {
              name: 'ctaButton',
              title: 'CTA Button',
              type: 'button',
            },
            {
              name: 'highlighted',
              title: 'Highlighted',
              type: 'boolean',
              description: 'Mark as recommended/popular plan',
              initialValue: false,
            },
            {
              name: 'badge',
              title: 'Badge',
              type: 'string',
              description: 'Optional badge text (e.g., "Most Popular")',
            },
          ],
          preview: {
            select: {
              name: 'name',
              amount: 'price.amount',
              currency: 'price.currency',
            },
            prepare({ name, amount, currency }) {
              return {
                title: name,
                subtitle: `${currency} ${amount}`,
              }
            },
          },
        },
      ],
      validation: (Rule) => Rule.min(1).max(6),
    },
  ],
  preview: {
    select: {
      title: 'heading',
      planCount: 'plans',
    },
    prepare({ title, planCount }) {
      return {
        title: title || 'Pricing Table',
        subtitle: planCount ? `${planCount.length} plans` : 'No plans',
      }
    },
  },
})
