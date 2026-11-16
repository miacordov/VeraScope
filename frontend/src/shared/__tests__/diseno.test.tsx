import { fireEvent, render, screen } from '@testing-library/react-native';

import { Desplegable, Texto } from '@/shared/ui';

describe('Desplegable', () => {
  it('muestra el resumen cerrado, abre el contenido y anuncia su estado', async () => {
    await render(
      <Desplegable titulo="Ver detalles" tituloAbierto="Ocultar detalles" resumen="p-valor">
        <Texto>contenido</Texto>
      </Desplegable>,
    );
    expect(screen.getByText('p-valor')).toBeOnTheScreen();
    expect(screen.queryByText('contenido')).toBeNull();
    expect(screen.getByRole('button', { name: 'Ver detalles' })).toBeCollapsed();

    await fireEvent.press(screen.getByRole('button', { name: 'Ver detalles' }));
    expect(screen.getByText('contenido')).toBeOnTheScreen();
    expect(screen.getByRole('button', { name: 'Ocultar detalles' })).toBeExpanded();

    await fireEvent.press(screen.getByRole('button', { name: 'Ocultar detalles' }));
    expect(screen.queryByText('contenido')).toBeNull();
  });
});
