"""
Tests for React + TypeScript parsing functionality
"""

import unittest
from code_chunker import CodeChunker
from code_chunker.models import ChunkType


class TestReactTypeScriptParser(unittest.TestCase):
    def setUp(self):
        self.chunker = CodeChunker()
        self.test_code = """
import React, { useState, useEffect, useContext } from 'react';
import { useRouter } from 'next/router';

// Props 类型定义
interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

// 函数组件
function Button({ onClick, children, variant = 'primary' }: ButtonProps) {
  return (
    <button 
      className={`btn btn-${variant}`} 
      onClick={onClick}
    >
      {children}
    </button>
  );
}

// 箭头函数组件 with React.FC
export const Card: React.FC<{
  title: string;
  content: string;
}> = ({ title, content }) => (
  <div className="card">
    <h2>{title}</h2>
    <p>{content}</p>
  </div>
);

// Context
const ThemeContext = React.createContext<{ theme: string; toggleTheme: () => void }>({
  theme: 'light',
  toggleTheme: () => {},
});

// Provider
export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };
  
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Hook
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// 自定义 Hook
export const useWindowSize = () => {
  const [size, setSize] = useState<{ width: number; height: number }>({
    width: 0,
    height: 0
  });
  
  useEffect(() => {
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return size;
};

// React.memo 组件
const MemoizedButton = React.memo(({ onClick, children }: ButtonProps) => {
  return (
    <button onClick={onClick}>
      {children}
    </button>
  );
});

// forwardRef 组件
const TextInput = React.forwardRef<HTMLInputElement, { label: string }>(
  (props, ref) => (
    <div>
      <label>{props.label}</label>
      <input ref={ref} type="text" />
    </div>
  )
);

// HOC
function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return (props: P) => {
    const isAuthenticated = true; // 假设有一个认证逻辑
    
    if (!isAuthenticated) {
      return <div>Please log in</div>;
    }
    
    return <Component {...props} />;
  };
}

// 使用 HOC
const AuthenticatedCard = withAuth(Card);

// 默认导出
export default function App() {
  const { width } = useWindowSize();
  
  return (
    <ThemeProvider>
      <div className="app">
        <h1>React TypeScript App</h1>
        <p>Window width: {width}px</p>
        <Button onClick={() => console.log('clicked')}>
          Click me
        </Button>
        <Card title="Hello" content="World" />
        <MemoizedButton onClick={() => console.log('memo clicked')}>
          Memoized Button
        </MemoizedButton>
        <TextInput label="Enter text" />
        <AuthenticatedCard title="Auth Card" content="Protected content" />
      </div>
    </ThemeProvider>
  );
}
"""

    def test_react_components(self):
        """Test React component detection"""
        result = self.chunker.parse(self.test_code, language='typescript')
        
        # 找出所有 COMPONENT 类型的 chunks
        components = [chunk for chunk in result.chunks if chunk.type == ChunkType.COMPONENT]
        component_names = [c.name for c in components]
        
        # 验证我们是否找到了所有组件
        self.assertIn('Button', component_names)
        self.assertIn('Card', component_names)
        self.assertIn('MemoizedButton', component_names)
        self.assertIn('TextInput', component_names)
        self.assertIn('App', component_names)
        
        # 验证组件元数据
        button = next(c for c in components if c.name == 'Button')
        self.assertEqual(button.metadata.get('component_type'), 'function')
        self.assertEqual(button.metadata.get('props_type'), 'ButtonProps')
        self.assertTrue(button.metadata.get('has_jsx'))
        
        card = next(c for c in components if c.name == 'Card')
        self.assertEqual(card.metadata.get('component_type'), 'fc')
        self.assertTrue(card.metadata.get('is_default_export', False) is False)
        self.assertTrue(card.metadata.get('has_jsx'))
        
        app = next(c for c in components if c.name == 'App')
        self.assertTrue(app.metadata.get('is_default_export', False))
        self.assertIn('useWindowSize', app.metadata.get('hooks_used', []))

    def test_react_hooks(self):
        """Test React hooks detection"""
        result = self.chunker.parse(self.test_code, language='typescript')
        
        # 找出所有 HOOK 类型的 chunks
        hooks = [chunk for chunk in result.chunks if chunk.type == ChunkType.HOOK]
        hook_names = [h.name for h in hooks]
        
        # 验证我们是否找到了所有 hooks
        self.assertIn('useTheme', hook_names)
        self.assertIn('useWindowSize', hook_names)
        
        # 验证 hook 元数据
        use_theme = next(h for h in hooks if h.name == 'useTheme')
        self.assertIn('useContext', use_theme.metadata.get('used_hooks', []))
        
        use_window_size = next(h for h in hooks if h.name == 'useWindowSize')
        self.assertIn('useState', use_window_size.metadata.get('used_hooks', []))
        self.assertIn('useEffect', use_window_size.metadata.get('used_hooks', []))

    def test_react_context(self):
        """Test React context detection"""
        result = self.chunker.parse(self.test_code, language='typescript')
        
        # 找出所有 CONTEXT 类型的 chunks
        contexts = [chunk for chunk in result.chunks if chunk.type == ChunkType.CONTEXT]
        context_names = [c.name for c in contexts]
        
        # 验证我们是否找到了所有 contexts
        self.assertIn('ThemeContext', context_names)
        
        # 验证 context 元数据
        theme_context = next(c for c in contexts if c.name == 'ThemeContext')
        self.assertEqual(theme_context.metadata.get('context_type'), '{ theme: string; toggleTheme: () => void }')

    def test_react_provider(self):
        """Test React provider detection"""
        result = self.chunker.parse(self.test_code, language='typescript')
        
        # 找出所有 PROVIDER 类型的 chunks
        providers = [chunk for chunk in result.chunks if chunk.type == ChunkType.PROVIDER]
        provider_names = [p.name for p in providers]
        
        # 验证我们是否找到了所有 providers
        self.assertIn('ThemeProvider', provider_names)
        
        # 验证 provider 元数据
        theme_provider = next(p for p in providers if p.name == 'ThemeProvider')
        self.assertTrue(theme_provider.metadata.get('has_jsx'))
        self.assertEqual(theme_provider.metadata.get('related_context'), 'ThemeContext')

    def test_react_hoc(self):
        """Test React HOC detection"""
        result = self.chunker.parse(self.test_code, language='typescript')
        
        # 找出所有 HOC 类型的 chunks
        hocs = [chunk for chunk in result.chunks if chunk.type == ChunkType.HOC]
        hoc_names = [h.name for h in hocs]
        
        # 验证我们是否找到了所有 HOCs
        self.assertIn('withAuth', hoc_names)
        
        # 验证 HOC 元数据
        with_auth = next(h for h in hocs if h.name == 'withAuth')
        self.assertTrue(with_auth.metadata.get('has_jsx'))

    def test_typescript_types(self):
        """Test TypeScript type detection"""
        result = self.chunker.parse(self.test_code, language='typescript')
        
        # 找出所有接口和类型
        interfaces = [chunk for chunk in result.chunks if chunk.type == ChunkType.CLASS and chunk.metadata.get('is_interface')]
        interface_names = [i.name for i in interfaces]
        
        # 验证我们是否找到了所有接口
        self.assertIn('ButtonProps', interface_names)
        
        # 验证接口元数据
        button_props = next(i for i in interfaces if i.name == 'ButtonProps')
        self.assertTrue(button_props.metadata.get('is_props'))


if __name__ == '__main__':
    unittest.main() 