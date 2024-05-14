#include <linux/module.h>     // included for all kernel modules
#include <linux/init.h>       // included for __init and __exit macros
#include <linux/kthread.h>    // included for threading related functions
#include <linux/sched.h>      // included to create tesk_struct
#include <linux/delay.h>      // included for the sleep/delay function in the thread

#include <linux/slab.h>	      // included for kmalloc
#include <linux/mm.h>
#include <linux/mm_rewind.h>

struct task_struct *rewind_kth;
unsigned long rewind_pf_cnt;
static LIST_HEAD(pf_rewind_list);

struct pf_rewind_info
{
	pid_t pid;
	unsigned int flags;
	unsigned long address;
	pte_t *pte;
	struct list_head list;
};

void add_on_rewind_list(struct vm_fault *vmf){
	// pf_rewind structure
	printk(KERN_INFO "REWIND(add): pid=%d, pte=0x%lx\n", vmf->vma->vm_mm->owner->pid, vmf->pte->pte);
}

int rewind_manager(void *tmp) {
	return 0;
}

int __init rewinder_init(void) {
	rewind_kth = kthread_create(rewind_manager, NULL, "rewinder_kth");
	rewind_pf_cnt = 0;

	if (rewind_kth != NULL) {
		wake_up_process(rewind_kth);
		printk(KERN_INFO "Rewinder kernel thread is running\n");
	} else {
		printk(KERN_INFO "Rewinder ERROR!\n");
		return -1;
	}

	return 0;
}

static void __exit rewinder_exit(void) {
	kthread_stop(rewind_kth);
	return;
}

module_init(rewinder_init)
module_exit(rewinder_exit)


