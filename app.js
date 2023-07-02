const app = new Vue({
  el: '#app',
  data: {
    maquinas: [
      { id: 1, nombre: 'Máquina 1', tipo: 'Tipo A', precio: 1000 },
      { id: 2, nombre: 'Máquina 2', tipo: 'Tipo B', precio: 1500 },
      { id: 3, nombre: 'Máquina 3', tipo: 'Tipo C', precio: 2000 }
    ],
    nuevaMaquina: {
      nombre: '',
      tipo: '',
      precio: null
    }
  },
  methods: {
    agregarMaquina() {
      // Genera un ID único para la nueva máquina
      const nuevoId = this.maquinas.length > 0 ? this.maquinas[this.maquinas.length - 1].id + 1 : 1;
      
      // Agrega la nueva máquina al arreglo
      this.maquinas.push({
        id: nuevoId,
        nombre: this.nuevaMaquina.nombre,
        tipo: this.nuevaMaquina.tipo,
        precio: this.nuevaMaquina.precio
      });
      
      // Limpia los campos del formulario
      this.nuevaMaquina.nombre = '';
      this.nuevaMaquina.tipo = '';
      this.nuevaMaquina.precio = null;
    }
  }
});
