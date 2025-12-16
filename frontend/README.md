# Constituent Briefing Modal - Frontend

A full-screen modal component for displaying AI-powered constituent briefings with comprehensive donor information, engagement analytics, and suggested actions.

## Features

- **Full-Screen Modal**: Responsive, iOS-inspired modal with smooth fade + scale animations
- **AI-Generated Summaries**: Intelligent constituent insights and relationship analysis
- **Giving Breakdown**: Complete donation history with charts and statistics
- **Engagement Timeline**: Interactive timeline of all interactions and touchpoints
- **Segment Classification**: Dynamic segmentation with criteria explanation
- **Suggested Actions**: AI-powered next steps with priority levels and reasoning
- **Generate Message CTA**: Quick action button to compose personalized outreach

## Components

### `ConstituentModal.tsx`
Main modal component with:
- Header with constituent name, contact info, and key stats
- Scrollable content area with multiple sections
- Footer with "Generate Message" CTA
- Framer Motion animations (fade + scale)
- Loading and error states

### `BriefingSection.tsx`
Reusable section components including:
- `BriefingSection`: Styled section container with icon and title
- `StatCard`: Metric display card with optional trend indicators
- `TimelineItem`: Timeline entry with icon, date, and description
- `Badge`: Status/category badge with color variants
- `ProgressBar`: Animated progress visualization

## API Endpoint

```
GET /api/constituents/:id/briefing
```

Returns a `ConstituentBriefing` object with:
- Constituent details
- AI-generated summary
- Key statistics
- Giving breakdown
- Engagement timeline
- Segment classification
- Suggested actions

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Date Formatting**: date-fns

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) (or the port you set in `FRONTEND_PORT`) to see the demo.

### Build

```bash
npm run build
npm start
```

## Usage

```tsx
import { ConstituentModal } from '@/components/ConstituentModal';

function MyPage() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        View Briefing
      </button>

      <ConstituentModal
        constituentId={1}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        onGenerateMessage={(id) => console.log('Generate message for:', id)}
      />
    </>
  );
}
```

## Customization

### Animations

Customize animations in `tailwind.config.js`:

```js
animation: {
  'fade-in': 'fadeIn 0.3s ease-out',
  'scale-in': 'scaleIn 0.3s ease-out',
  'slide-up': 'slideUp 0.3s ease-out',
}
```

### Colors

Adjust the color scheme by modifying the Tailwind classes in the components.

### API Integration

To connect to your backend, update the fetch call in `/app/api/constituents/[id]/briefing/route.ts`:

```typescript
const response = await fetch(`${process.env.BACKEND_URL}/api/constituents/${id}/briefing`);
const data = await response.json();
```

## Type Definitions

All TypeScript interfaces are defined in `/types/constituent.ts`:

- `Constituent`
- `ConstituentBriefing`
- `GivingBreakdown`
- `EngagementTimeline`
- `Segment`
- `SuggestedAction`

## Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   └── constituents/
│   │       └── [id]/
│   │           └── briefing/
│   │               └── route.ts      # API endpoint
│   ├── layout.tsx                    # Root layout
│   ├── page.tsx                      # Demo page
│   └── globals.css                   # Global styles
├── components/
│   ├── ConstituentModal.tsx          # Main modal component
│   └── BriefingSection.tsx           # Section components
├── types/
│   └── constituent.ts                # TypeScript interfaces
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Future Enhancements

- Real-time data updates
- Export briefing to PDF
- Inline message composition
- Comparison view for multiple constituents
- Historical briefing versions
- Mobile-optimized layout
- Accessibility improvements (ARIA labels, keyboard navigation)

## License

MIT
