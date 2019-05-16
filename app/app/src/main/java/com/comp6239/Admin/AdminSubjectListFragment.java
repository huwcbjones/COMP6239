package com.comp6239.Admin;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.Fragment;
import android.support.v7.widget.GridLayoutManager;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.Log;
import android.view.GestureDetector;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.R;
import com.comp6239.Tutor.TutorViewProfileActivity;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * A fragment representing a list of Items.
 * <p/>
 * Activities containing this fragment MUST implement the {@link OnListFragmentInteractionListener}
 * interface.
 */
public class AdminSubjectListFragment extends Fragment {

    // TODO: Customize parameter argument names
    private static final String ARG_COLUMN_COUNT = "column-count";
    // TODO: Customize parameters
    private int mColumnCount = 1;
    private OnListFragmentInteractionListener mListener;
    private RecyclerView mRecyclerView;
    private BackendRequestController apiBackend;


    /**
     * Mandatory empty constructor for the fragment manager to instantiate the
     * fragment (e.g. upon screen orientation changes).
     */
    public AdminSubjectListFragment() {
    }

    // TODO: Customize parameter initialization
    @SuppressWarnings("unused")
    public static AdminSubjectListFragment newInstance(int columnCount) {
        AdminSubjectListFragment fragment = new AdminSubjectListFragment();
        Bundle args = new Bundle();
        args.putInt(ARG_COLUMN_COUNT, columnCount);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (getArguments() != null) {
            mColumnCount = getArguments().getInt(ARG_COLUMN_COUNT);
        }

        apiBackend = BackendRequestController.getInstance(getContext());
    }


    public void createSubjectList() {
        Call<List<Subject>> subjectList = apiBackend.apiService.getAllSubjects();
        subjectList.enqueue(new Callback<List<Subject>>() {
            @Override
            public void onResponse(Call<List<Subject>> call, Response<List<Subject>> response) {
                mRecyclerView.setAdapter(new AdminMySubjectRecyclerViewAdapter(response.body(), mListener));
            }

            @Override
            public void onFailure(Call<List<Subject>> call, Throwable t) {
                Toast toast = Toast.makeText(getContext(), "There was a network error searching for tutors! Try again later!", Toast.LENGTH_LONG);
                toast.show();
            }
        });
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_subject_list, container, false);

        Context context = view.getContext();
        mRecyclerView = view.findViewById(R.id.tutor_search_list);
        if (mColumnCount <= 1) {
            mRecyclerView.setLayoutManager(new LinearLayoutManager(context));
        } else {
            mRecyclerView.setLayoutManager(new GridLayoutManager(context, mColumnCount));
        }

        FloatingActionButton fab = view.findViewById(R.id.addSubjectFab);

        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAddSubject();
            }
        });

        createSubjectList();

        final GestureDetector gesture = new GestureDetector(getActivity(),
                new GestureDetector.SimpleOnGestureListener() {

                    @Override
                    public boolean onDown(MotionEvent e) {
                        return true;
                    }

                    @Override
                    public boolean onFling(MotionEvent e1, MotionEvent e2, float velocityX,
                                           float velocityY) {
                        final int SWIPE_MIN_DISTANCE = 120;
                        final int SWIPE_MAX_OFF_PATH = 250;
                        final int SWIPE_THRESHOLD_VELOCITY = 200;
                        try {
                            if (Math.abs(e1.getX() - e2.getX()) > SWIPE_MAX_OFF_PATH)
                                return false;
                            if (e1.getY() - e2.getY() > SWIPE_MIN_DISTANCE
                                    && Math.abs(velocityY) > SWIPE_THRESHOLD_VELOCITY) {
                                Log.i("Swipe", "Down to Up");
                            } else if (e2.getY() - e1.getY() > SWIPE_MIN_DISTANCE
                                    && Math.abs(velocityY) > SWIPE_THRESHOLD_VELOCITY) {
                                Log.i("Swipe", "Up to Down");
                                createSubjectList();
                            }
                        } catch (Exception e) {
                            // nothing
                        }
                        return super.onFling(e1, e2, velocityX, velocityY);
                    }
                });
        view.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                return gesture.onTouchEvent(event);
            }
        });

        return view;
    }

    public void triggerAddSubject() {
        LayoutInflater layoutInflater = LayoutInflater.from(getContext());
        View promptView = layoutInflater.inflate(R.layout.dialog_add_subject, null);
        AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(getContext());
        alertDialogBuilder.setView(promptView);

        final EditText editText = promptView.findViewById(R.id.subject_name_edittext);
        // setup a dialog window
        alertDialogBuilder.setCancelable(false)
                .setPositiveButton("Add Subject", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        if(TextUtils.isEmpty(editText.getText())) {
                            Toast toast = Toast.makeText(getContext(), "Please enter a Subject name before submitting!", Toast.LENGTH_LONG);
                            toast.show();
                            return;
                        }
                        Call<Void> createSub = apiBackend.apiService.createNewSubject(new Subject(editText.getText().toString()));
                        createSub.enqueue(new Callback<Void>() {
                            @Override
                            public void onResponse(Call<Void> call, Response<Void> response) {
                                Toast toast = Toast.makeText(getContext(), "Successfully created new subject!", Toast.LENGTH_LONG);
                                toast.show();
                                createSubjectList();
                            }

                            @Override
                            public void onFailure(Call<Void> call, Throwable t) {
                                Toast toast = Toast.makeText(getContext(), "Failed to access the server!", Toast.LENGTH_LONG);
                                toast.show();
                            }
                        });

                    }
                })
                .setNegativeButton("Cancel",
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int id) {
                                dialog.cancel();
                            }
                        });

        // create an alert dialog
        AlertDialog alert = alertDialogBuilder.create();
        alert.show();
    }


    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof OnListFragmentInteractionListener) {
            mListener = (OnListFragmentInteractionListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnListFragmentInteractionListener");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
    }

    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     * <p/>
     * See the Android Training lesson <a href=
     * "http://developer.android.com/training/basics/fragments/communicating.html"
     * >Communicating with Other Fragments</a> for more information.
     */
    public interface OnListFragmentInteractionListener {
        void onSubjectListFragmentInteraction(Subject item);
    }
}
