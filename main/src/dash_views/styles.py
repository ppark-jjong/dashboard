from typing import Dict, Any


class StyleManager:
    """스타일 관리를 위한 중앙화된 매니저 클래스"""

    @staticmethod
    def get_common_styles() -> Dict[str, Any]:
        return {
            'card': {
                'padding': '1.5rem',
                'borderRadius': '16px',
                'boxShadow': '0 10px 25px rgba(0,0,0,0.08)',
                'backgroundColor': 'white',
                'border': 'none',
                'margin': '1rem 0',
                'width': '100%'
            },
            'search_input': {
                'width': '300px',
                'borderRadius': '8px',
                'border': '1px solid #e2e8f0',
                'padding': '0.5rem 1rem',
                'fontSize': '0.95rem',
                'marginBottom': '1rem'
            },
            'refresh_button': {
                'backgroundColor': '#3b82f6',
                'border': '1px solid #3b82f6',
                'borderRadius': '8px',
                'padding': '0.5rem 1rem',
                'fontSize': '0.9rem',
                'marginRight': '0.75rem',
                'cursor': 'pointer',
                'color': 'white',
                'fontWeight': '600',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'transition': 'all 0.3s ease',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'
            },
            'table': {
                'cell': {
                    'textAlign': 'center',
                    'fontSize': '0.9rem',
                    'padding': '0.75rem',
                    'fontFamily': 'Arial, sans-serif',
                    'color': '#2c3e50',
                    'borderRight': '1px solid #e2e8f0',
                    'borderLeft': '1px solid #e2e8f0',
                    'minWidth': '120px',
                    'width': '150px',
                    'maxWidth': '300px'
                },
                'header': {
                    'backgroundColor': '#f8fafc',
                    'fontWeight': '600',
                    'border': '1px solid #e2e8f0',
                    'borderBottom': '2px solid #3b82f6',
                    'textAlign': 'center',
                    'fontSize': '0.95rem',
                    'color': '#1e293b',
                    'height': '56px',
                    'cursor': 'pointer',
                    'padding': '0 1rem',
                    'position': 'relative'
                }
            },
            'pagination': {
                'container': {
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'gap': '0.5rem',
                    'padding': '1rem',
                    'backgroundColor': '#f8fafc',
                    'borderRadius': '12px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'
                },
                'button': {
                    'height': '40px',
                    'minWidth': '40px',
                    'padding': '0 0.75rem',
                    'fontSize': '0.875rem',
                    'backgroundColor': 'white',
                    'border': '1px solid #e2e8f0',
                    'color': '#64748b',
                    'cursor': 'pointer',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'borderRadius': '6px',
                    'transition': 'all 0.3s ease',
                    'fontWeight': '500',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.04)'
                }
            }
        }
