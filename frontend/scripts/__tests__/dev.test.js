const path = require('node:path');

const { elegirIp, origenesCors, pythonDelVenv } = require('../dev');

const ip = (address, extra = {}) => ({ address, family: 'IPv4', internal: false, ...extra });

describe('elegirIp', () => {
  it('elige la IP de la Wi-Fi y descarta el loopback y los adaptadores virtuales', () => {
    const interfaces = {
      'Loopback Pseudo-Interface 1': [ip('127.0.0.1', { internal: true })],
      'vEthernet (WSL)': [ip('172.20.48.1')],
      'VirtualBox Host-Only Network': [ip('192.168.56.1')],
      'Wi-Fi': [{ address: 'fe80::1', family: 'IPv6', internal: false }, ip('192.168.1.34')],
    };
    expect(elegirIp(interfaces)).toBe('192.168.1.34');
  });

  it('prefiere 192.168.x sobre 10.x y 172.16–31.x', () => {
    expect(elegirIp({ a: [ip('10.0.0.5')], b: [ip('172.16.0.2')], c: [ip('192.168.0.9')] })).toBe('192.168.0.9');
    expect(elegirIp({ a: [ip('172.16.0.2')], b: [ip('10.0.0.5')] })).toBe('10.0.0.5');
  });

  it('acepta family numérica (Node antiguo)', () => {
    expect(elegirIp({ eth0: [{ address: '10.1.2.3', family: 4, internal: false }] })).toBe('10.1.2.3');
  });

  it('devuelve null si no hay una IP privada', () => {
    expect(elegirIp({ lo: [ip('127.0.0.1', { internal: true })], wan: [ip('8.8.8.8')] })).toBeNull();
  });
});

describe('pythonDelVenv', () => {
  it('usa Scripts\\python.exe en Windows y bin/python en el resto', () => {
    expect(pythonDelVenv('venv', true)).toBe(path.join('venv', 'Scripts', 'python.exe'));
    expect(pythonDelVenv('venv', false)).toBe(path.join('venv', 'bin', 'python'));
  });
});

describe('origenesCors', () => {
  it('incluye localhost, 127.0.0.1 y la IP local en el puerto de Expo', () => {
    expect(origenesCors('192.168.1.34')).toBe(
      'http://localhost:8081,http://127.0.0.1:8081,http://192.168.1.34:8081',
    );
    expect(origenesCors(null)).toBe('http://localhost:8081,http://127.0.0.1:8081');
  });

  it('usa el puerto alternativo cuando el 8081 está ocupado', () => {
    expect(origenesCors(null, 8082)).toBe('http://localhost:8082,http://127.0.0.1:8082');
  });
});
