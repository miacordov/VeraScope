import { useQuery } from '@tanstack/react-query';

import { api } from '@/shared/api/cliente';
import type { DemoId } from '@/shared/api/tipos';

/** Guion de una demo con la llave de frontend/CLAUDE.md §8 (`['demo', id]`). `null` no dispara la llamada. */
export function useDemo(id: DemoId | null) {
  return useQuery({
    queryKey: ['demo', id ?? 'ninguna'],
    queryFn: ({ signal }) => api.demo(id as DemoId, signal),
    enabled: id !== null,
  });
}
