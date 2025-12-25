import React from 'react';
import type { A2UIComponentData, A2UIRoot } from './types';

// specific component implementations
const Container: React.FC<{ children?: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '8px', ...style }}>{children}</div>
);

const Text: React.FC<{ content: string; style?: React.CSSProperties }> = ({ content, style }) => (
  <span style={style}>{content}</span>
);

const Button: React.FC<{ label: string; onClick?: () => void; style?: React.CSSProperties }> = ({ label, onClick, style }) => (
  <button onClick={onClick} style={{ padding: '0.5rem 1rem', cursor: 'pointer', ...style }}>
    {label}
  </button>
);

const Row: React.FC<{ children?: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ display: 'flex', flexDirection: 'row', gap: '8px', ...style }}>{children}</div>
);

const Column: React.FC<{ children?: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', ...style }}>{children}</div>
);

const Card: React.FC<{ title?: string; children?: React.ReactNode; style?: React.CSSProperties }> = ({ title, children, style }) => (
  <div style={{ padding: '1rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', borderRadius: '8px', background: 'white', color: 'black', ...style }}>
    {title && <h3 style={{ marginTop: 0 }}>{title}</h3>}
    {children}
  </div>
);

const Image: React.FC<{ src: string; alt?: string; style?: React.CSSProperties }> = ({ src, alt, style }) => (
  <img src={src} alt={alt || ''} style={{ maxWidth: '100%', borderRadius: '4px', ...style }} />
);

// Component Registry
const COMPONENT_MAP: Record<string, React.FC<any>> = {
  Container,
  Text,
  Button,
  Row,
  Column,
  Card,
  Image,
  Box: Container, // alias
};

interface RendererProps {
  component: A2UIComponentData;
}

export const A2UIComponentRenderer: React.FC<RendererProps> = ({ component }) => {
  const Component = COMPONENT_MAP[component.type];

  if (!Component) {
    console.warn(`Unknown A2UI component type: ${component.type}`);
    return <div style={{ color: 'red' }}>Unknown Component: {component.type}</div>;
  }

  const { children, props, id } = component;
  
  // Recursively render children
  const renderedChildren = children?.map((child, idx) => (
    <A2UIComponentRenderer key={child.id || idx} component={child} />
  ));

  return (
    <Component {...props} id={id}>
      {renderedChildren}
    </Component>
  );
};

export const A2UIRootRenderer: React.FC<{ data: A2UIRoot }> = ({ data }) => {
  if (!data || !data.root) return null;
  return <A2UIComponentRenderer component={data.root} />;
};
