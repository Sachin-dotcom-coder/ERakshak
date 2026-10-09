import { createFileRoute } from '@tanstack/react-router';
import { CommandCentre } from '@/components/traffic/CommandCentre';

export const Route = createFileRoute('/')({
  component: CommandCentre,
});
