import { render, screen } from '@testing-library/react-native';

import { LogoVeraScope } from '../LogoVeraScope';

describe('LogoVeraScope', () => {
  it('es una imagen con etiqueta en español para lectores de pantalla', async () => {
    await render(<LogoVeraScope tamano={48} />);
    const logo = screen.getByLabelText('Logo de VeraScope');
    expect(logo).toBeTruthy();
    expect(logo.props.accessibilityRole).toBe('image');
  });
});
