# sirex_utils.py
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from IPython.display import display, clear_output
import ipywidgets as widgets
from matplotlib.gridspec import GridSpec

# ============================================================================
# CONFIGURAÇÕES GLOBAIS
# ============================================================================
CORES = {
    1: '#FF6347',   # tomato
    2: '#FFA500',   # orange
    3: '#FFF68F',   # khaki1
    4: '#7CCD7C',   # palegreen3
    5: '#4682B4'    # steelblue
}

def carregar_dados(caminho_shapefile="Otto_Overall_SC.shp"):
    """Carrega o shapefile e retorna um GeoDataFrame."""
    gdf = gpd.read_file(caminho_shapefile)
    return gdf

# ============================================================================
# FUNÇÃO DE PLOTAGEM DO MAPA (sem legenda)
# ============================================================================
def plot_dim(data, coluna, titulo, ax):
    """
    Plota um mapa de uma dimensão/indicador sem legenda.
    """
    # Garantir que a coluna seja numérica e inteira
    valores = pd.to_numeric(data[coluna], errors='coerce')
    
    # Mapear cores: NaN -> cinza claro
    cores_plot = [CORES.get(int(x), 'lightgrey') if pd.notna(x) else 'lightgrey' for x in valores]
    
    data.plot(ax=ax, color=cores_plot, edgecolor='none', linewidth=0)
    
    # Ajustar limites (Santa Catarina)
    ax.set_xlim(-54, -48)
    ax.set_ylim(-30, -25)
    ax.set_aspect('equal')
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.axis('off')

# ============================================================================
# FUNÇÃO PARA CRIAR LEGENDA HORIZONTAL (5 blocos juntos, textos só nas pontas)
# ============================================================================
def criar_legenda_horizontal(fig, width_ratios=None):
    """
    Adiciona uma legenda horizontal na parte inferior da figura.
    Retorna o eixo da legenda.
    """
    if width_ratios is None:
        width_ratios = [1]*5
    
    # Criar um eixo para a legenda (ocupando toda a largura)
    ax_leg = fig.add_axes([0.1, 0.05, 0.3, 0.1])  # [left, bottom, width, height]
    
    # Largura de cada bloco (proporcional)
    total = sum(width_ratios)
    x_pos = 0
    for i, (valor, cor) in enumerate(CORES.items()):
        block_width = width_ratios[i] / total
        rect = plt.Rectangle((x_pos, 0.2), block_width, 0.6, facecolor=cor, edgecolor='white', linewidth=1)
        ax_leg.add_patch(rect)
        x_pos += block_width
    
    # Textos apenas no primeiro e último bloco
    ax_leg.text(0.0, 0.5, 'Menor segurança hídrica', 
                ha='left', va='center', fontsize=11, fontweight='bold', transform=ax_leg.transAxes)
    ax_leg.text(1, 0.5, 'Maior segurança hídrica', 
                ha='right', va='center', fontsize=11, fontweight='bold', transform=ax_leg.transAxes)
    
    ax_leg.set_xlim(0, 1)
    ax_leg.set_ylim(0, 1)
    ax_leg.axis('off')
    return ax_leg

# ============================================================================
# FUNÇÃO PARA PLOTAR INDICADOR COM 3 MAPAS + LEGENDA
# ============================================================================
def plot_indicador(data, prefixo, titulo_superior=None):
    """
    Gera uma figura com três mapas (2000, 2010, 2020) e uma legenda horizontal 
    centralizada, com largura reduzida e blocos mais espessos.
    
    Parâmetros:
    - data: GeoDataFrame com os dados
    - prefixo: string, ex: 'P_' para população, 'S_' para rede, etc.
    - titulo_superior: (não usado) mantido para compatibilidade, mas ignorado
    """
    # Cria a figura com GridSpec: 2 linhas, 3 colunas
    # height_ratios: primeira linha (mapas) 5x mais alta que a segunda (legenda)
    fig = plt.figure(figsize=(15, 6))
    gs = GridSpec(2, 3, height_ratios=[5, 1], hspace=0.2, top=0.95, bottom=0.1)

    # Eixos para os mapas (primeira linha, cada coluna)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    anos = ['2000', '2010', '2020']

    # Plota cada mapa
    for i, ano in enumerate(anos):
        col = f"{prefixo}{ano}"
        if col in data.columns:
            plot_dim(data, col, ano, axes[i])

    # Eixo da legenda (segunda linha, ocupando as 3 colunas)
    ax_leg = fig.add_subplot(gs[1, :])

    # ------------------------------------------------------------
    # AJUSTE DA LARGURA DA LEGENDA: reduz para 55% e centraliza
    # ------------------------------------------------------------
    pos = ax_leg.get_position()
    nova_largura = 0.55
    novo_left = 0.5 - nova_largura / 2
    ax_leg.set_position([novo_left, pos.y0, nova_largura, pos.height])

    # ------------------------------------------------------------
    # DESENHO DOS BLOCOS (5 blocos justapostos)
    # ------------------------------------------------------------
    x_pos = 0
    block_width = 1 / 5
    altura_bloco = 0.4
    y_base = 0.3  # para centralizar verticalmente no eixo

    for valor, cor in CORES.items():
        rect = plt.Rectangle((x_pos, y_base), block_width, altura_bloco,
                             facecolor=cor, edgecolor='white', linewidth=1)
        ax_leg.add_patch(rect)
        x_pos += block_width

    # ------------------------------------------------------------
    # TEXTOS NAS EXTREMIDADES
    # ------------------------------------------------------------
    ax_leg.text(block_width * 0.0, y_base + altura_bloco + 0.1, 'Menor segurança hídrica',
                ha='left', va='center', fontsize=12, fontweight='bold')
    ax_leg.text(block_width * 5.0, y_base + altura_bloco + 0.1, 'Maior segurança hídrica',
                ha='right', va='center', fontsize=12, fontweight='bold')

    # ------------------------------------------------------------
    # CONFIGURAÇÕES FINAIS DO EIXO DA LEGENDA
    # ------------------------------------------------------------
    ax_leg.set_xlim(0, 1)
    ax_leg.set_ylim(0, 1)
    ax_leg.axis('off')

    # Título removido – agora será fornecido pelo markdown
    # plt.suptitle(titulo_superior, fontsize=16, fontweight='bold', y=0.98)
    plt.show()

# ============================================================================
# FUNÇÃO DE CÁLCULO DO ÍNDICE (igual, mas com ajuste de tipo)
# ============================================================================
def calcular_ish_ano(df, ano, wp, wr, wa, wk, wf, ws, wd1, wd2, wd3, wd4):
    """
    Calcula o índice para um ano específico.
    Retorna uma série com valores 1-5 (categorias).
    """
    p_col = f'P_{ano}'
    s_col = f'S_{ano}'
    a_col = f'A_{ano}'
    k_col = f'K_{ano}'
    q_col = f'Q_{ano}'
    f_col = f'F_{ano}'
    d_col = f'D_{ano}'
    
    # Converter para numérico
    df_temp = df.copy()
    for col in [p_col, s_col, a_col, k_col, q_col, f_col, d_col]:
        if col in df_temp.columns:
            df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce')
    
    # Dimensões
    d1_num = (df_temp[p_col].fillna(0) * wp + df_temp[s_col].fillna(0) * wr)
    d1_den = (df_temp[p_col].notna() * wp + df_temp[s_col].notna() * wr)
    d1 = np.where(d1_den > 0, d1_num / d1_den, np.nan)
    
    d2_num = (df_temp[a_col].fillna(0) * wa + df_temp[k_col].fillna(0) * wk)
    d2_den = (df_temp[a_col].notna() * wa + df_temp[k_col].notna() * wk)
    d2 = np.where(d2_den > 0, d2_num / d2_den, np.nan)
    
    d4_num = (df_temp[f_col].fillna(0) * wf + df_temp[d_col].fillna(0) * ws)
    d4_den = (df_temp[f_col].notna() * wf + df_temp[d_col].notna() * ws)
    d4 = np.where(d4_den > 0, d4_num / d4_den, np.nan)
    
    d3 = df_temp[q_col].values
    
    # Índice final
    numerador = (np.nan_to_num(d1, nan=0) * wd1 + 
                 np.nan_to_num(d2, nan=0) * wd2 + 
                 np.nan_to_num(d3, nan=0) * wd3 + 
                 np.nan_to_num(d4, nan=0) * wd4)
    denominador = ( (~np.isnan(d1)) * wd1 + 
                    (~np.isnan(d2)) * wd2 + 
                    (~np.isnan(d3)) * wd3 + 
                    (~np.isnan(d4)) * wd4 )
    indice = np.where(denominador > 0, numerador / denominador, np.nan)
    
    # Arredondar e limitar entre 1 e 5
    indice = np.round(indice).clip(1, 5)
    indice = pd.Series(indice).astype('Int64')
    return indice

# ============================================================================
# FUNÇÃO PARA CRIAR A INTERFACE INTERATIVA (com legenda igual)
# ============================================================================
def criar_interface_interativa(gdf):
    """
    Cria e retorna os widgets e a função de atualização.
    Layout: primeira linha com os indicadores, segunda linha com os pesos das dimensões.
    Sliders com largura reduzida (200px) e sincronização automática para soma=1.
    """
    # Definição da largura padrão para os sliders
    slider_width = '250px'

    # --- Sliders dos indicadores com layout ---
    w_pop = widgets.FloatSlider(value=0.5, min=0, max=1, step=0.05,
                                 description='População:', layout=widgets.Layout(width=slider_width))
    w_rede = widgets.FloatSlider(value=0.5, min=0, max=1, step=0.05,
                                  description='Rede:', layout=widgets.Layout(width=slider_width))
    w_agr = widgets.FloatSlider(value=0.5, min=0, max=1, step=0.05,
                                 description='Agricultura:', layout=widgets.Layout(width=slider_width))
    w_pork = widgets.FloatSlider(value=0.5, min=0, max=1, step=0.05,
                                  description='Suína:', layout=widgets.Layout(width=slider_width))
    w_cheia = widgets.FloatSlider(value=0.5, min=0, max=1, step=0.05,
                                   description='Cheias:', layout=widgets.Layout(width=slider_width))
    w_seca = widgets.FloatSlider(value=0.5, min=0, max=1, step=0.05,
                                  description='Secas:', layout=widgets.Layout(width=slider_width))

    # --- Sliders dos pesos das dimensões com layout ---
    w_dim1 = widgets.FloatSlider(value=0.25, min=0, max=1, step=0.05,
                                  description='Humana:', layout=widgets.Layout(width=slider_width))
    w_dim2 = widgets.FloatSlider(value=0.25, min=0, max=1, step=0.05,
                                  description='Econômica:', layout=widgets.Layout(width=slider_width))
    w_dim3 = widgets.FloatSlider(value=0.25, min=0, max=1, step=0.05,
                                  description='Ecossistêmica:', layout=widgets.Layout(width=slider_width))
    w_dim4 = widgets.FloatSlider(value=0.25, min=0, max=1, step=0.05,
                                  description='Resiliência:', layout=widgets.Layout(width=slider_width))

    # ------------------------------------------------------------
    # Sincronização dos pares de indicadores (soma = 1)
    # ------------------------------------------------------------

    # Dimensão Humana
    def sync_humana(change):
        # Evita loop infinito
        if hasattr(sync_humana, 'lock') and sync_humana.lock:
            return
        sync_humana.lock = True
        try:
            if change['owner'] is w_pop:
                novo_valor = round(1 - w_pop.value, 2)
                w_rede.value = novo_valor
            elif change['owner'] is w_rede:
                novo_valor = round(1 - w_rede.value, 2)
                w_pop.value = novo_valor
        finally:
            sync_humana.lock = False

    w_pop.observe(sync_humana, names='value')
    w_rede.observe(sync_humana, names='value')
    sync_humana.lock = False

    # Dimensão Econômica
    def sync_economica(change):
        if hasattr(sync_economica, 'lock') and sync_economica.lock:
            return
        sync_economica.lock = True
        try:
            if change['owner'] is w_agr:
                w_pork.value = round(1 - w_agr.value, 2)
            elif change['owner'] is w_pork:
                w_agr.value = round(1 - w_pork.value, 2)
        finally:
            sync_economica.lock = False

    w_agr.observe(sync_economica, names='value')
    w_pork.observe(sync_economica, names='value')
    sync_economica.lock = False

    # Dimensão Resiliência
    def sync_resiliencia(change):
        if hasattr(sync_resiliencia, 'lock') and sync_resiliencia.lock:
            return
        sync_resiliencia.lock = True
        try:
            if change['owner'] is w_cheia:
                w_seca.value = round(1 - w_cheia.value, 2)
            elif change['owner'] is w_seca:
                w_cheia.value = round(1 - w_seca.value, 2)
        finally:
            sync_resiliencia.lock = False

    w_cheia.observe(sync_resiliencia, names='value')
    w_seca.observe(sync_resiliencia, names='value')
    sync_resiliencia.lock = False

    # ------------------------------------------------------------
    # Sincronização das quatro dimensões (soma = 1)
    # ------------------------------------------------------------
    def sync_dimensoes(change):
        if hasattr(sync_dimensoes, 'lock') and sync_dimensoes.lock:
            return
        sync_dimensoes.lock = True
        try:
            # Lista de widgets na ordem
            dim_widgets = [w_dim1, w_dim2, w_dim3, w_dim4]
            # Identifica qual foi alterado
            alterado = change['owner']
            idx_alterado = dim_widgets.index(alterado)
            novo_valor_alterado = alterado.value

            # Soma dos demais (valores atuais)
            soma_outros = 0
            for i, w in enumerate(dim_widgets):
                if i != idx_alterado:
                    soma_outros += w.value

            # Se a soma dos outros for zero, distribui igualmente entre os demais
            if soma_outros == 0:
                novo_valor_restante = (1 - novo_valor_alterado) / 3
                for i, w in enumerate(dim_widgets):
                    if i != idx_alterado:
                        w.value = round(novo_valor_restante, 2)
            else:
                # Ajusta proporcionalmente
                fator = (1 - novo_valor_alterado) / soma_outros
                for i, w in enumerate(dim_widgets):
                    if i != idx_alterado:
                        novo = w.value * fator
                        w.value = round(novo, 2)
        finally:
            sync_dimensoes.lock = False

    # Conecta a função a todos os quatro sliders
    w_dim1.observe(sync_dimensoes, names='value')
    w_dim2.observe(sync_dimensoes, names='value')
    w_dim3.observe(sync_dimensoes, names='value')
    w_dim4.observe(sync_dimensoes, names='value')
    sync_dimensoes.lock = False

    # --- Widget de saída ---
    out = widgets.Output()

    def update_maps(change=None):
        with out:
            clear_output(wait=True)

            # Coletar pesos
            wp = w_pop.value
            wr = w_rede.value
            wa = w_agr.value
            wk = w_pork.value
            wf = w_cheia.value
            ws = w_seca.value
            wd1 = w_dim1.value
            wd2 = w_dim2.value
            wd3 = w_dim3.value
            wd4 = w_dim4.value

            # Calcular para cada ano
            gdf_calc = gdf.copy()
            gdf_calc['O_2000_cat'] = calcular_ish_ano(gdf_calc, '2000', wp, wr, wa, wk, wf, ws, wd1, wd2, wd3, wd4)
            gdf_calc['O_2010_cat'] = calcular_ish_ano(gdf_calc, '2010', wp, wr, wa, wk, wf, ws, wd1, wd2, wd3, wd4)
            gdf_calc['O_2020_cat'] = calcular_ish_ano(gdf_calc, '2020', wp, wr, wa, wk, wf, ws, wd1, wd2, wd3, wd4)

            # Criar figura com GridSpec
            fig = plt.figure(figsize=(15, 7))
            gs = GridSpec(2, 3, height_ratios=[5, 1], hspace=0.2, top=0.92, bottom=0.1)
            axes = [fig.add_subplot(gs[0, i]) for i in range(3)]

            # Plotar mapas
            plot_dim(gdf_calc, 'O_2000_cat', '2000', axes[0])
            plot_dim(gdf_calc, 'O_2010_cat', '2010', axes[1])
            plot_dim(gdf_calc, 'O_2020_cat', '2020', axes[2])

            # --- Eixo da legenda ---
            ax_leg = fig.add_subplot(gs[1, :])
            pos = ax_leg.get_position()
            nova_largura = 0.55
            novo_left = 0.5 - nova_largura/2
            ax_leg.set_position([novo_left, pos.y0, nova_largura, pos.height])

            # Desenhar blocos
            x_pos = 0
            block_width = 1/5
            altura_bloco = 0.4
            y_base = 0.3
            # Nota: usamos CORES.values() para manter a ordem 1,2,3,4,5
            for cor in CORES.values():
                rect = plt.Rectangle((x_pos, y_base), block_width, altura_bloco,
                                     facecolor=cor, edgecolor='white', linewidth=1)
                ax_leg.add_patch(rect)
                x_pos += block_width

            # Textos
            ax_leg.text(block_width*0.1, y_base + altura_bloco + 0.1, 'Menor segurança hídrica',
                        ha='left', va='center', fontsize=12, fontweight='bold')
            ax_leg.text(block_width*4.9, y_base + altura_bloco + 0.1, 'Maior segurança hídrica',
                        ha='right', va='center', fontsize=12, fontweight='bold')

            ax_leg.set_xlim(0, 1)
            ax_leg.set_ylim(0, 1)
            ax_leg.axis('off')

            plt.suptitle('Índice Geral de Segurança Hídrica', fontsize=16, fontweight='bold', y=0.98)
            plt.show()

    # Conectar todos os sliders à função de update
    for w in [w_pop, w_rede, w_agr, w_pork, w_cheia, w_seca, w_dim1, w_dim2, w_dim3, w_dim4]:
        w.observe(update_maps)

    # --- LAYOUT EM DUAS LINHAS ---
    # Primeira linha: grupos de indicadores
    humana_box = widgets.VBox([
        widgets.HTML("<b>Dimensão Humana</b>"),
        w_pop,
        w_rede
    ])
    economica_box = widgets.VBox([
        widgets.HTML("<b>Dimensão Econômica</b>"),
        w_agr,
        w_pork
    ])
    resiliencia_box = widgets.VBox([
        widgets.HTML("<b>Dimensão Resiliência</b>"),
        w_cheia,
        w_seca
    ])
    linha1 = widgets.HBox([humana_box, economica_box, resiliencia_box])

    # Segunda linha: pesos das dimensões
    dim1_box = widgets.VBox([widgets.HTML("<b>Humana</b>"), w_dim1])
    dim2_box = widgets.VBox([widgets.HTML("<b>Econômica</b>"), w_dim2])
    dim3_box = widgets.VBox([widgets.HTML("<b>Ecossistêmica</b>"), w_dim3])
    dim4_box = widgets.VBox([widgets.HTML("<b>Resiliência</b>"), w_dim4])
    linha2 = widgets.HBox([dim1_box, dim2_box, dim3_box, dim4_box])

    # Empilhar as linhas verticalmente
    controles = widgets.VBox([linha1, linha2])

    return controles, out, update_maps