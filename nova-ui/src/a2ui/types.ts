export interface A2UIProps {
  [key: string]: any;
}

export interface A2UIComponentData {
  type: string;
  props?: A2UIProps;
  children?: A2UIComponentData[];
  id?: string;
}

export interface A2UIRoot {
  root: A2UIComponentData;
}
