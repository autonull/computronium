// Minimal type declarations for golden-layout
declare module "golden-layout" {
  export interface Config {
    content: ContentItem[];
    settings?: Settings;
    dimensions?: Dimensions;
    labels?: Labels;
  }

  export interface ContentItem {
    type: "row" | "column" | "stack" | "component";
    width?: number;
    height?: number;
    content?: ContentItem[];
    componentName?: string;
    componentState?: unknown;
    title?: string;
    isClosable?: boolean;
    id?: string;
  }

  export interface Settings {
    showPopoutIcon?: boolean;
    showMaximiseIcon?: boolean;
    showCloseIcon?: boolean;
    constrainDragToContainer?: boolean;
    reorderEnabled?: boolean;
    selectionEnabled?: boolean;
    tabOverlapAllowance?: number;
  }

  export interface Dimensions {
    borderWidth?: number;
    minItemHeight?: number;
    minItemWidth?: number;
    headerHeight?: number;
    dragProxyWidth?: number;
    dragProxyHeight?: number;
  }

  export interface Labels {
    tabDropPlaceholder?: string;
    tabDragIndicator?: string;
  }

  export interface ItemConfig extends ContentItem {}

  export class Item {
    config: ItemConfig;
    isComponent: boolean;
    isRow: boolean;
    isColumn: boolean;
    isStack: boolean;
    parent: Item | null;
    contentItems: Item[];
    container: Container | null;
    element: JQuery;
    on(event: string, listener: (...args: any[]) => void): void;
    off(event: string, listener: (...args: any[]) => void): void;
  }

  export class Container {
    config: ItemConfig;
    parent: Item;
    element: JQuery;
    title: string;
    isClosable: boolean;
    on(event: string, listener: (...args: any[]) => void): void;
    off(event: string, listener: (...args: any[]) => void): void;
    getElement(): JQuery;
    extendState(state: unknown): void;
  }

  export class Tab {
    contentItem: Item;
    element: JQuery;
    isActive: boolean;
    on(event: string, listener: (...args: any[]) => void): void;
  }

  export type ComponentFactory = (container: Container, state: unknown) => void;

  export class GoldenLayout {
    constructor(container: HTMLElement | JQuery, config: Config);
    registerComponent(name: string, factory: ComponentFactory): void;
    loadLayout(config: ContentItem[]): void;
    toConfig(): Config;
    destroy(): void;
    on(event: string, listener: (...args: any[]) => void): void;
    off(event: string, listener: (...args: any[]) => void): void;
    root: Item;
  }

  // Also export as default
  export default GoldenLayout;
}

// CSS imports
declare module "golden-layout/dist/goldenlayout-base.css" {
  const content: string;
  export default content;
}
declare module "golden-layout/dist/goldenlayout-light-theme.css" {
  const content: string;
  export default content;
}

// JQuery shim for golden-layout
interface JQuery {
  append(...args: any[]): this;
  remove(): this;
  on(event: string, handler: (e: any) => void): this;
  off(event: string, handler: (e: any) => void): this;
  css(properties: Record<string, string>): this;
  find(selector: string): JQuery;
  children(): JQuery;
}