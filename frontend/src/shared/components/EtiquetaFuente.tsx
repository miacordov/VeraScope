import { lineaFuente } from '@/shared/format';
import type { AnalyzeRespuesta } from '@/shared/api/tipos';
import { Texto } from '@/shared/ui';

/** Fuente, celda, periodo, descarga e índice en una línea; todo viene de la respuesta (§13). */
export function EtiquetaFuente({ analisis }: { analisis: AnalyzeRespuesta }) {
  const texto = lineaFuente(analisis);
  return (
    <Texto variante="pequeno" suave accessibilityLabel={`Fuente: ${texto}`}>
      {texto}
    </Texto>
  );
}
